from __future__ import annotations

"""
交互式管理 CLI：
- 用户与管理员注册
- 部门 / 小组注册与绑定
- 项目注册与授权
- 按日期区间批量触发 GA4 / GSC / Yandex 数据拉取

用法示例：

  uv run python -m app.manage user add-admin
  uv run python -m app.manage user add
  uv run python -m app.manage department add
  uv run python -m app.manage group add
  uv run python -m app.manage auth grant-project
  uv run python -m app.manage ingest ga4-range
"""

import argparse
import getpass
from datetime import date, timedelta

import requests
from sqlalchemy.orm import Session
import questionary

from app.db import SessionLocal
from app import models
from app.auth.security import hash_password
from app.config import get_settings


def prompt(text: str, default: str | None = None) -> str:
  tip = f"{text}"
  if default is not None:
    tip += f" [{default}]"
  tip += ": "
  value = input(tip).strip()
  if not value and default is not None:
    return default
  return value


def prompt_password(text: str = "请输入密码") -> str:
  while True:
    pwd = getpass.getpass(f"{text}: ")
    if len(pwd) < 6:
      print("密码过短，请至少使用 6 位。")
      continue
    confirm = getpass.getpass("请再次输入密码进行确认: ")
    if pwd != confirm:
      print("两次输入不一致，请重试。")
      continue
    return pwd


def get_db() -> Session:
  return SessionLocal()


# 用户 / 管理员


def cmd_user_add_admin(_args: argparse.Namespace) -> None:
  print("=== 创建管理员账号 ===")
  email = prompt("管理员邮箱（用于登录）")
  name = prompt("管理员姓名", default="Admin")
  password = prompt_password()

  db = get_db()
  try:
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
      print("该邮箱已存在用户记录，取消创建。")
      return

    user = models.User(
      email=email,
      name=name,
      password_hash=hash_password(password),
      is_admin=True,
      is_active=True,
    )
    db.add(user)
    db.commit()
    print(f"已创建管理员用户：{email}")
  finally:
    db.close()


def cmd_user_add(_args: argparse.Namespace) -> None:
  print("=== 创建普通用户 ===")
  email = prompt("用户邮箱（用于登录）")
  name = prompt("用户姓名")
  password = prompt_password()

  db = get_db()
  try:
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
      print("该邮箱已存在用户记录，取消创建。")
      return

    user = models.User(
      email=email,
      name=name,
      password_hash=hash_password(password),
      is_admin=False,
      is_active=True,
    )
    db.add(user)
    db.commit()
    print(f"已创建普通用户：{email}")
  finally:
    db.close()


def cmd_user_list(_args: argparse.Namespace) -> None:
  db = get_db()
  try:
    users = db.query(models.User).order_by(models.User.id.asc()).all()
    if not users:
      print("当前还没有用户。")
      return
    print("ID\t管理员\t激活\t邮箱\t姓名")
    for u in users:
      print(
        f"{u.id}\t{'Y' if u.is_admin else 'N'}\t{'Y' if u.is_active else 'N'}\t{u.email}\t{u.name}"
      )
  finally:
    db.close()


# 部门 / 小组


def cmd_department_add(_args: argparse.Namespace) -> None:
  print("=== 创建部门 ===")
  name = prompt("部门名称")
  db = get_db()
  try:
    exists = db.query(models.Department).filter(models.Department.name == name).first()
    if exists:
      print("该部门已存在。")
      return
    dep = models.Department(name=name)
    db.add(dep)
    db.commit()
    print(f"已创建部门：{name}")
  finally:
    db.close()


def cmd_group_add(_args: argparse.Namespace) -> None:
  print("=== 在部门下创建小组 ===")
  db = get_db()
  try:
    deps = db.query(models.Department).order_by(models.Department.id.asc()).all()
    if not deps:
      print("当前还没有部门，请先创建部门。")
      return
    print("可选部门：")
    for d in deps:
      print(f"{d.id}\t{d.name}")
    dep_id = int(prompt("请输入所属部门 ID"))
    dep = db.query(models.Department).filter(models.Department.id == dep_id).first()
    if not dep:
      print("部门不存在。")
      return
    name = prompt("小组名称")
    grp = models.Group(department_id=dep.id, name=name)
    db.add(grp)
    db.commit()
    print(f"已在部门 {dep.name} 下创建小组：{name}")
  finally:
    db.close()


def cmd_user_assign_department(_args: argparse.Namespace) -> None:
  print("=== 将用户加入部门 ===")
  db = get_db()
  try:
    users = db.query(models.User).order_by(models.User.id.asc()).all()
    deps = db.query(models.Department).order_by(models.Department.id.asc()).all()
    if not users or not deps:
      print("需要至少一个用户和一个部门。")
      return
    print("用户列表：")
    for u in users:
      print(f"{u.id}\t{u.email}\t{'管理员' if u.is_admin else ''}")
    user_id = int(prompt("请输入用户 ID"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
      print("用户不存在。")
      return
    print("部门列表：")
    for d in deps:
      print(f"{d.id}\t{d.name}")
    dep_id = int(prompt("请输入部门 ID"))
    dep = db.query(models.Department).filter(models.Department.id == dep_id).first()
    if not dep:
      print("部门不存在。")
      return
    exists = (
      db.query(models.UserDepartment)
      .filter(
        models.UserDepartment.user_id == user.id,
        models.UserDepartment.department_id == dep.id,
      )
      .first()
    )
    if exists:
      print("该用户已在该部门中。")
      return
    link = models.UserDepartment(user_id=user.id, department_id=dep.id)
    db.add(link)
    db.commit()
    print(f"已将用户 {user.email} 加入部门 {dep.name}。")
  finally:
    db.close()


def cmd_user_assign_group(_args: argparse.Namespace) -> None:
  print("=== 将用户加入小组 ===")
  db = get_db()
  try:
    users = db.query(models.User).order_by(models.User.id.asc()).all()
    groups = (
      db.query(models.Group)
      .join(models.Department, models.Group.department_id == models.Department.id)
      .order_by(models.Group.id.asc())
      .all()
    )
    if not users or not groups:
      print("需要至少一个用户和一个小组。")
      return
    print("用户列表：")
    for u in users:
      print(f"{u.id}\t{u.email}\t{'管理员' if u.is_admin else ''}")
    user_id = int(prompt("请输入用户 ID"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
      print("用户不存在。")
      return
    print("小组列表：")
    for g in groups:
      # g.department 可能未配置 relationship 名称，这里仅展示 group id/name
      print(f"{g.id}\t{g.name}")
    group_id = int(prompt("请输入小组 ID"))
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
      print("小组不存在。")
      return
    exists = (
      db.query(models.UserGroup)
      .filter(
        models.UserGroup.user_id == user.id,
        models.UserGroup.group_id == group.id,
      )
      .first()
    )
    if exists:
      print("该用户已在该小组中。")
      return
    link = models.UserGroup(user_id=user.id, group_id=group.id)
    db.add(link)
    db.commit()
    print(f"已将用户 {user.email} 加入小组 {group.name}。")
  finally:
    db.close()


# 项目与权限


def cmd_project_add(_args: argparse.Namespace) -> None:
  print("=== 注册项目（站点） ===")
  project_key = prompt("项目唯一标识（英文、短横线等）")
  name = prompt("项目名称")
  domain = prompt("站点域名（例如 example.com）")
  ga4_property_id = prompt("GA4 Property ID（可选）", default="")
  gsc_property = prompt("GSC Property（可选，形如 https://example.com/）", default="")
  yandex_host = prompt("Yandex host（可选）", default="")

  db = get_db()
  try:
    exists = (
      db.query(models.Project)
      .filter(models.Project.project_key == project_key)
      .first()
    )
    if exists:
      print("该 project_key 已存在，取消创建。")
      return
    project = models.Project(
      project_key=project_key,
      name=name,
      domain=domain,
      ga4_property_id=ga4_property_id or None,
      gsc_property=gsc_property or None,
      yandex_host=yandex_host or None,
      status="active",
    )
    db.add(project)
    db.commit()
    print(f"已创建项目 {name}（ID={project.id}，key={project_key}）")
  finally:
    db.close()


def cmd_auth_grant_project(_args: argparse.Namespace) -> None:
  print("=== 为用户授权项目 ===")
  db = get_db()
  try:
    users = db.query(models.User).order_by(models.User.id.asc()).all()
    projects = db.query(models.Project).order_by(models.Project.id.asc()).all()
    if not users or not projects:
      print("需要至少一个用户和一个项目才能授权。")
      return
    print("用户列表：")
    for u in users:
      print(f"{u.id}\t{u.email}\t{'管理员' if u.is_admin else ''}")
    user_id = int(prompt("请输入要授权的用户 ID"))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
      print("用户不存在。")
      return
    print("项目列表：")
    for p in projects:
      print(f"{p.id}\t{p.name}\t{p.domain}")
    project_id = int(prompt("请输入要授权访问的项目 ID"))
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
      print("项目不存在。")
      return
    exists = (
      db.query(models.UserProjectPermission)
      .filter(
        models.UserProjectPermission.user_id == user.id,
        models.UserProjectPermission.project_id == project.id,
      )
      .first()
    )
    if exists:
      print("该用户已拥有该项目访问权限。")
      return
    perm = models.UserProjectPermission(user_id=user.id, project_id=project.id)
    db.add(perm)
    db.commit()
    print(f"已为用户 {user.email} 授权项目 {project.name}。")
  finally:
    db.close()


# 批量数据拉取


def _iter_dates(start: date, end: date):
  cur = start
  while cur <= end:
    yield cur
    cur += timedelta(days=1)


def _ingest_range(source: str, project_key: str, start: date, end: date) -> None:
  settings = get_settings()
  base_url = f"http://localhost:{settings.port}"
  print(f"=== 批量拉取 {source} 数据 ===")
  print(f"项目 key: {project_key}，日期范围: {start} ~ {end}")

  mapping = {
    "ga4": [
      "/api/admin/ingest/ga4-daily",
      "/api/admin/ingest/ga4-channel-daily",
      "/api/admin/ingest/ga4-page-daily",
    ],
    "gsc": [
      "/api/admin/ingest/gsc-daily",
      "/api/admin/ingest/gsc-query-daily",
      "/api/admin/ingest/gsc-page-daily",
    ],
    "yandex": [
      "/api/admin/ingest/yandex-daily",
      "/api/admin/ingest/yandex-query-daily",
    ],
  }

  paths = mapping.get(source)
  if not paths:
    print(f"未知数据源：{source}")
    return

  for d in _iter_dates(start, end):
    date_str = d.isoformat()
    print(f"处理日期：{date_str}")
    for path in paths:
      url = f"{base_url}{path}"
      try:
        resp = requests.post(
          url,
          params={"project_key": project_key, "target_date": date_str},
          timeout=30,
        )
        if resp.status_code == 200:
          print(f"  [OK] {path}")
        else:
          print(f"  [FAIL] {path} status={resp.status_code} detail={resp.text[:200]}")
      except Exception as exc:
        print(f"  [ERROR] {path} 异常: {exc}")


def cmd_ingest_ga4_range(_args: argparse.Namespace) -> None:
  print("=== 批量拉取 GA4 数据（日期区间）===")
  project_key = prompt("项目 key（projects.project_key）")
  start_str = prompt("开始日期 (YYYY-MM-DD)")
  end_str = prompt("结束日期 (YYYY-MM-DD)")
  start = date.fromisoformat(start_str)
  end = date.fromisoformat(end_str)
  _ingest_range("ga4", project_key, start, end)


def cmd_ingest_gsc_range(_args: argparse.Namespace) -> None:
  print("=== 批量拉取 GSC 数据（日期区间）===")
  project_key = prompt("项目 key（projects.project_key）")
  start_str = prompt("开始日期 (YYYY-MM-DD)")
  end_str = prompt("结束日期 (YYYY-MM-DD)")
  start = date.fromisoformat(start_str)
  end = date.fromisoformat(end_str)
  _ingest_range("gsc", project_key, start, end)


def cmd_ingest_yandex_range(_args: argparse.Namespace) -> None:
  print("=== 批量拉取 Yandex 数据（日期区间）===")
  project_key = prompt("项目 key（projects.project_key）")
  start_str = prompt("开始日期 (YYYY-MM-DD)")
  end_str = prompt("结束日期 (YYYY-MM-DD)")
  start = date.fromisoformat(start_str)
  end = date.fromisoformat(end_str)
  _ingest_range("yandex", project_key, start, end)


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="SEO 看板管理 CLI")
  subparsers = parser.add_subparsers(dest="command", required=True)

  # user
  user_parser = subparsers.add_parser("user", help="用户相关操作")
  user_sub = user_parser.add_subparsers(dest="sub", required=True)
  user_sub.add_parser("add-admin", help="创建管理员账号").set_defaults(
    func=cmd_user_add_admin
  )
  user_sub.add_parser("add", help="创建普通用户").set_defaults(func=cmd_user_add)
  user_sub.add_parser("list", help="列出用户").set_defaults(func=cmd_user_list)

  # department
  dep_parser = subparsers.add_parser("department", help="部门相关操作")
  dep_sub = dep_parser.add_subparsers(dest="sub", required=True)
  dep_sub.add_parser("add", help="创建部门").set_defaults(func=cmd_department_add)

  # group
  grp_parser = subparsers.add_parser("group", help="小组相关操作")
  grp_sub = grp_parser.add_subparsers(dest="sub", required=True)
  grp_sub.add_parser("add", help="在部门下创建小组").set_defaults(func=cmd_group_add)
  grp_sub.add_parser("assign-user", help="将用户加入小组").set_defaults(
    func=cmd_user_assign_group
  )

  # project / auth
  proj_parser = subparsers.add_parser("project", help="项目（站点）相关操作")
  proj_sub = proj_parser.add_subparsers(dest="sub", required=True)
  proj_sub.add_parser("add", help="注册项目").set_defaults(func=cmd_project_add)

  auth_parser = subparsers.add_parser("auth", help="权限相关操作")
  auth_sub = auth_parser.add_subparsers(dest="sub", required=True)
  auth_sub.add_parser("grant-project", help="为用户授权项目访问").set_defaults(
    func=cmd_auth_grant_project
  )

  # ingest
  ingest_parser = subparsers.add_parser("ingest", help="批量数据拉取")
  ingest_sub = ingest_parser.add_subparsers(dest="sub", required=True)
  ingest_sub.add_parser("ga4-range", help="按日期区间拉取 GA4 数据").set_defaults(
    func=cmd_ingest_ga4_range
  )
  ingest_sub.add_parser("gsc-range", help="按日期区间拉取 GSC 数据").set_defaults(
    func=cmd_ingest_gsc_range
  )
  ingest_sub.add_parser("yandex-range", help="按日期区间拉取 Yandex 数据").set_defaults(
    func=cmd_ingest_yandex_range
  )

  return parser

def interactive_main() -> None:
  """友好的总交互入口：不带任何参数运行时，提供上下移动、回车确认、可返回上级菜单的 TUI。"""
  menu_structure: list[tuple[str, list[tuple[str, callable | None]]]] = [
    (
      "👤 用户与组织管理",
      [
        ("⭐ 创建管理员账号", lambda: cmd_user_add_admin(argparse.Namespace())),
        ("➕ 创建普通用户", lambda: cmd_user_add(argparse.Namespace())),
        ("📋 查看用户列表", lambda: cmd_user_list(argparse.Namespace())),
        ("🏢 创建部门", lambda: cmd_department_add(argparse.Namespace())),
        ("👥 在部门下创建小组", lambda: cmd_group_add(argparse.Namespace())),
        ("🔗 将用户加入部门", lambda: cmd_user_assign_department(argparse.Namespace())),
        ("🔗 将用户加入小组", lambda: cmd_user_assign_group(argparse.Namespace())),
      ],
    ),
    (
      "📂 项目与权限管理",
      [
        ("📌 注册项目（站点）", lambda: cmd_project_add(argparse.Namespace())),
        ("🔑 为用户授权项目访问", lambda: cmd_auth_grant_project(argparse.Namespace())),
      ],
    ),
    (
      "📈 批量数据拉取",
      [
        ("🔵 按日期区间拉取 GA4 数据", lambda: cmd_ingest_ga4_range(argparse.Namespace())),
        ("🟢 按日期区间拉取 GSC 数据", lambda: cmd_ingest_gsc_range(argparse.Namespace())),
        ("🟣 按日期区间拉取 Yandex 数据", lambda: cmd_ingest_yandex_range(argparse.Namespace())),
      ],
    ),
  ]

  def run_action(action: callable | None) -> None:
    if not action:
      return
    try:
      action()
    except KeyboardInterrupt:
      print("\n操作已中断，已返回菜单。")
    except Exception as exc:  # noqa: BLE001
      print(f"\n执行过程中发生错误: {exc}")

  while True:
    logo = (
      "╔════════════════════════════════════════════╗\n"
      "║        ★ 多站点 SEO 数据看板管理 ★         ║\n"
      "╚════════════════════════════════════════════╝"
    )

    # 先打印“Logo”边框，使其不被 questionary 自带的前缀符号打断
    print(logo)

    # 选择一级菜单（questionary 会在下一行以 “? ” 开头显示提示，不再破坏边框）
    root_choice = questionary.select(
      "【主菜单】请选择要操作的功能模块（↑↓ 移动，Enter 确认，Esc 取消）：",
      choices=[
        questionary.Choice(menu_structure[0][0], value="sec_0"),
        questionary.Choice(menu_structure[1][0], value="sec_1"),
        questionary.Choice(menu_structure[2][0], value="sec_2"),
        questionary.Choice("❌ 退出管理菜单", value="quit"),
      ],
    ).ask()

    if root_choice is None or root_choice == "quit":
      print("已退出管理菜单。")
      return

    section_index = int(root_choice.split("_")[1])
    section_label, actions = menu_structure[section_index]

    # 选择子菜单
    print(logo)
    sub_choices = [
      questionary.Choice(label, value=str(i))
      for i, (label, _action) in enumerate(actions)
    ]
    sub_choices.append(questionary.Choice("🔙 返回上级菜单", value="back"))
    sub_choices.append(questionary.Choice("❌ 退出管理菜单", value="quit"))

    sub_choice = questionary.select(
      f"【{section_label}】请选择要执行的操作（↑↓ 移动，Enter 确认，Esc 取消）：",
      choices=sub_choices,
    ).ask()

    if sub_choice is None or sub_choice == "back":
      continue
    if sub_choice == "quit":
      print("已退出管理菜单。")
      return

    idx = int(sub_choice)
    _label, action = actions[idx]
    run_action(action)


def main() -> None:
  # 不带参数时，进入菜单式交互入口，方便运维使用
  import sys

  if len(sys.argv) == 1:
    try:
      interactive_main()
    except KeyboardInterrupt:
      print("\n已退出管理菜单。")
    return

  parser = build_parser()
  args = parser.parse_args()
  func = getattr(args, "func", None)
  if not func:
    parser.print_help()
    return
  func(args)


if __name__ == "__main__":
  main()


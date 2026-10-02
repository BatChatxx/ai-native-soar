"""
Seed script: import a DFIR-report-based ransomware incident for review & development.

Run from inside the backend container:
    docker exec soar_backend python seed_dfir.py

The report describes an EtherRAT + TukTuk C2 campaign ending in The Gentleman
ransomware deployment.
"""
import sys
from datetime import datetime, timezone

# Make sure we can import app modules when run as a script
sys.path.insert(0, "/app")

from models.database import get_session_local  # noqa: E402
from models.models import Incident, IncidentEvent, IncidentComment, IncidentObservable  # noqa: E402


REPORT = {
    "number": "INC-2026-05-11-ETHERRAT-TUKTUK-001",
    "title": "EtherRAT + TukTuk C2 导致 The Gentleman 勒索软件部署",
    "severity": "critical",
    "status": "new",
    "source_type": "DFIR Report Flash Alert",
    "detection_source": "ransomware / double-extortion",
    "description": (
        "2026年4月观察到一起入侵事件：用户执行伪装成 Sysinternals RAMMap 的恶意 MSI，"
        "部署 EtherRAT。EtherRAT 通过 Ethereum 区块链（EtherHiding）动态更新 C2 配置，"
        "随后下载 Node.js 运行时并建立持久化。攻击者后续部署 TukTuk 恶意软件"
        "（伪装成 Greenshot 等合法二进制，通过 DLL 侧加载），利用 SaaS 平台"
        "（ClickHouse、Supabase）和区块链（Arweave）作为 C2/死投解析。攻击者使用 "
        "合法外观的远程管理工具（RMM）进行横向移动，通过 Rclone 将数据外泄至云存储服务，"
        "最终通过恶意 GPO 在域内广泛部署 The Gentlemen 勒索软件。"
    ),
    "attack_chain": [
        {
            "phase": "initial_access",
            "technique": "T1204 User Execution",
            "description": "用户执行伪装成 Sysinternals RAMMap 的恶意 MSI 安装程序。",
            "ioc": "RAMMap.msi",
        },
        {
            "phase": "execution",
            "technique": "T1059.003 Command and Scripting Interpreter: Windows Command Shell",
            "description": "MSI 执行后启动 cmd.exe 并运行 MVnVmUYj.cmd。",
            "ioc": "MVnVmUYj.cmd",
        },
        {
            "phase": "persistence",
            "technique": "T1547.001 Registry Run Keys / Startup Folder",
            "description": "通过注册表 Run 键建立持久化，使用 node.exe 加载 A7Pnj975bl.cfg。",
            "ioc": "A7Pnj975bl.cfg",
        },
        {
            "phase": "command_and_control",
            "technique": "T1102 Web Service",
            "description": (
                "EtherRAT 通过 1rpc.io 查询 Ethereum 智能合约获取 C2 配置；"
                "TukTuk 使用 ClickHouse、Supabase、Arweave 等作为 C2/死投解析。"
            ),
        },
        {
            "phase": "defense_evasion",
            "technique": "T1218.011 Signed Binary Proxy Execution: Rundll32",
            "description": "通过 comsvcs.dll 转储 LSASS 内存。",
        },
        {
            "phase": "credential_access",
            "technique": "T1003.001 OS Credential Dumping: LSASS Memory",
            "description": "使用 Mimikatz、LSASS/NTDS 转储、Kerberoasting 获取凭据。",
        },
        {
            "phase": "discovery",
            "technique": "T1046 Network Service Discovery",
            "description": "使用 SoftPerfect Network Scanner 进行网络扫描；使用 Windows 原生工具进行系统、AV、域、LDAP 侦察。",
        },
        {
            "phase": "lateral_movement",
            "technique": "T1021 Remote Services",
            "description": "使用 NetExec (nxc) 进行 SMB 横向移动和凭据转储；使用合法外观的远程管理工具横向部署。",
        },
        {
            "phase": "exfiltration",
            "technique": "T1567.002 Exfiltration to Cloud Storage",
            "description": "使用 Rclone 将大量敏感数据外泄至云存储服务。",
        },
        {
            "phase": "impact",
            "technique": "T1486 Data Encrypted for Impact",
            "description": (
                "通过恶意 GPO 在域内广泛部署 The Gentlemen 勒索软件，"
                "禁用杀毒软件、添加 AV 排除、停止虚拟机、删除卷影副本、清除事件日志。"
            ),
        },
    ],
    "ioc_domains": [
        "1rpc.io",
        "witch-skins-lip-coal.trycloudflare.com",
        "fields-pct-easier-vancouver.trycloudflare.com",
        "howto-tar-naturals-coordination.trycloudflare.com",
        "workshop-lighting-protective-customs.trycloudflare.com",
        "vefbdzzuaadnascpeqcn.supabase.co",
        "k135neflez.westus3.azure.clickhouse.cloud",
        "borjumaniya.store",
    ],
    "ethereum_contracts": [
        "0xdf0b529043ef7a2bb9111bad26de624a326bacf9",
        "0x5953f27F044779a3AFCd2BF56a4B712583Dd2E4e",
    ],
    "arweave_drive_id": "a6278417-39f4-407e-90bf-599f74726e66",
    "hashes": {
        "RAMMap.msi": {
            "md5": "73ce2438d4ed475e03727b7b000d2794",
            "sha1": "3d5ee8429ef00824c0351cba507dfeb92b54f83b",
            "sha256": "d9487fdc097f770e5661f9e5dee130068cb179d33716abff1a21c8cb901f25a6",
        },
        "MVnVmUYj.cmd": {
            "md5": "b2d51212744f404714fd909e87254d98",
            "sha1": "c98ee41f09ae079a5643626f57eb84f92205bb2b",
            "sha256": "8c2665adf8bfab65463f2a9bd1b7bb0231de3f5c1e6a2e51479e44aaac2e7bf0",
        },
        "A7Pnj975bl.cfg": {
            "md5": "c92cf9a1af5b1fe25cdcb8771ce52be4",
            "sha1": "b44c8084b88d31113ee51758740eb84c251bdae8",
            "sha256": "4142d5efd4ea2abab77f2f0a917610e2ff976bf9e19d7ad1e9156eccdc5412db",
        },
        "log4net.dll": {
            "md5": "f985b8d6d635c266fc4779dad77aa75c",
            "sha1": "ba80d7b038758a129861e1e498e462cc3d68ae20",
            "sha256": "19021e53b9929fdf4b7d0e0707434d56bb73c1a9b7403c8837b44d1c417198dc",
        },
        "smokymo.msi": {
            "md5": "b188fbc6ff5557767e73e4c883a553a3",
            "sha1": "aa9218994798ae31a19d3e7e39cfac2e2ee55840",
            "sha256": "1795eacd2c58894ccdd6be8854fe6456c3b069a3a873432343b57b475b256aee",
        },
    },
    "recommended_actions": [
        "隔离受影响主机，尤其是域控制器和关键服务器。",
        "重置被泄露的服务账户和管理员账户密码。",
        "检查并移除未授权的 RMM 工具（如 remote management tool）。",
        "审查并阻止与已知 IOC 相关的出站连接。",
        "检查 GPO 是否被篡改，特别是通过 SYSVOL/NETLOGON 执行计划任务的 GPO。",
        "从备份恢复受勒索软件影响的数据，确保备份未被加密。",
        "进行全网威胁狩猎，重点关注 EtherRAT 和 TukTuk 的持久化和 C2 机制。",
    ],
    "reference": "https://thedfirreport.com/2026/05/11/flash-alert-etherrat-and-tuktuk-c2-end-in-the-gentleman-ransomware/",
}


def seed():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Incident).filter(Incident.number == REPORT["number"]).first()
        if existing:
            print(f"Already seeded: {REPORT['number']} (id={existing.id})")
            return

        now = datetime.now(timezone.utc)

        incident = Incident(
            number=REPORT["number"],
            title=REPORT["title"],
            description=REPORT["description"],
            severity=REPORT["severity"],
            status="open",
            priority="critical",
            source_type=REPORT["source_type"],
            detection_source=REPORT["detection_source"],
            created_at=now,
            updated_at=now,
        )
        db.add(incident)
        db.flush()  # get incident.id

        # attack_chain -> timeline events
        for step in REPORT["attack_chain"]:
            db.add(
                IncidentEvent(
                    incident_id=incident.id,
                    title=f"[{step['phase']}] {step['technique']}",
                    description=step["description"],
                    timestamp=now,
                )
            )

        # domains -> observables
        for d in REPORT["ioc_domains"]:
            db.add(
                IncidentObservable(
                    incident_id=incident.id,
                    observable_type="domain",
                    observable_value=d,
                    observed_at=now,
                )
            )

        # ethereum contracts -> observables
        for c in REPORT["ethereum_contracts"]:
            db.add(
                IncidentObservable(
                    incident_id=incident.id,
                    observable_type="ethereum_contract",
                    observable_value=c,
                    observed_at=now,
                )
            )

        # arweave drive id -> observable
        db.add(
            IncidentObservable(
                incident_id=incident.id,
                observable_type="arweave_drive_id",
                observable_value=REPORT["arweave_drive_id"],
                observed_at=now,
            )
        )

        # hashes -> observables
        for fname, h in REPORT["hashes"].items():
            if h.get("md5"):
                db.add(
                    IncidentObservable(
                        incident_id=incident.id,
                        observable_type="hash_md5",
                        observable_value=h["md5"],
                        file_name=fname,
                        observed_at=now,
                    )
                )
            if h.get("sha1"):
                db.add(
                    IncidentObservable(
                        incident_id=incident.id,
                        observable_type="hash_sha1",
                        observable_value=h["sha1"],
                        file_name=fname,
                        observed_at=now,
                    )
                )
            if h.get("sha256"):
                db.add(
                    IncidentObservable(
                        incident_id=incident.id,
                        observable_type="hash_sha256",
                        observable_value=h["sha256"],
                        file_name=fname,
                        observed_at=now,
                    )
                )

        # recommended actions -> a single analyst comment
        db.add(
            IncidentComment(
                incident_id=incident.id,
                content="Recommended actions:\n- " + "\n- ".join(REPORT["recommended_actions"]),
                created_at=now,
            )
        )

        db.commit()
        print(f"Seeded incident: {incident.number} (id={incident.id})")
        print(f"  events: {len(REPORT['attack_chain'])}")
        print(f"  observables: {len(REPORT['ioc_domains']) + len(REPORT['ethereum_contracts']) + 1 + sum(3 for _ in REPORT['hashes'])}")
        print(f"  comments: 1")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

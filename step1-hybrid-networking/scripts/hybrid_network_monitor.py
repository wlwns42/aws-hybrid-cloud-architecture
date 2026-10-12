import boto3
import requests
import json
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")

ec2_client = boto3.client("ec2", region_name=AWS_REGION)

def send_slack_alert(channel_url: str, message: str):
    if not channel_url:
        logging.warning("Slack Webhook URL 미설정: %s", message)
        return
    payload = {"text": message}
    try:
        res = requests.post(channel_url, json=payload, timeout=5)
        res.raise_for_status()
    except Exception as e:
        logging.error("Slack 알림 발송 실패: %s", e)

def check_vpn_tunnel_status():
    logging.info("AWS VPN 터널 상태 점검 시작...")
    response = ec2_client.describe_vpn_connections()
    
    for vpn in response.get("VpnConnections", []):
        vpn_id = vpn["VpnConnectionId"]
        state = vpn["State"]
        telemetry = vpn.get("VgwTelemetry", [])
        
        down_tunnels = []
        for tunnel in telemetry:
            outside_ip = tunnel.get("OutsideIpAddress")
            tunnel_status = tunnel.get("Status")
            status_message = tunnel.get("StatusDescription", "")
            
            if tunnel_status != "UP":
                down_tunnels.append(f"• IP: {outside_ip} (상태: {tunnel_status}, 상세: {status_message})")
                
        if down_tunnels:
            alert_msg = (
                f":warning: *[AWS Hybrid Network Alert] VPN 터널 장애 감지*\n"
                f"• VPN ID: `{vpn_id}` (Connection State: {state})\n"
                f"• 비정상 터널 목록:\n" + "\n".join(down_tunnels) + "\n"
                f"• 점검 시각: {datetime.utcnow().isoformat()}Z"
            )
            logging.error(alert_msg)
            send_slack_alert(SLACK_WEBHOOK_URL, alert_msg)
        else:
            logging.info("VPN ID %s: 모든 터널 상태 정상 (UP)", vpn_id)

if __name__ == "__main__":
    check_vpn_tunnel_status()
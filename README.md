\# Step 1. AWS x On-Premise 하이브리드 네트워킹 아키텍처 \& IaC



\## 1. 아키텍처 개요

온프레미스 IDC(통신망/폐쇄망)와 AWS VPC 간의 통신 안정성을 보장하기 위한 하이브리드 네트워크 설계:

\- \*\*Direct Connect (Active):\*\* 대용량 트래픽 및 저지연 전용선 연결

\- \*\*Site-to-Site VPN (Standby):\*\* 회선 장애 발생 시 BGP 기반 자동 우회(Failover)

\- \*\*Transit Gateway (TGW):\*\* 다중 VPC 및 IDC 간 허브 앤 스포크 라우팅 단일화



\## 2. 포함된 구성

\* `terraform/main.tf`: VPC, Private Subnet, Transit Gateway 프로비저닝 코드

\* `scripts/hybrid\_network\_monitor.py`: VPN 터널 헬스체크 및 Slack 웹훅 경보 발송 스크립트


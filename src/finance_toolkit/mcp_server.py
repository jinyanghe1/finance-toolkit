#!/usr/bin/env python3
"""
Finance Toolkit - MCP Server

用法:
    # Claude Code 配置 (settings.json)
    {
        "mcpServers": {
            "finance-toolkit": {
                "command": "python",
                "args": ["-m", "finance_toolkit.mcp_server"]
            }
        }
    }

    # Claude Desktop 配置
    {
        "finance-toolkit": {
            "command": "python",
            "args": ["-m", "finance_toolkit.mcp_server"]
        }
    }
"""

import json
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from finance_toolkit import CompanyAnalyzer
from finance_toolkit.data import search_stocks, fetch_company


class MCPServer:
    """MCP 服务器 - 处理 JSON-RPC 请求"""

    def __init__(self):
        self.analyzer = CompanyAnalyzer()

    def handle_request(self, request: dict) -> dict:
        """处理 MCP 请求"""
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "finance-toolkit",
                        "version": "0.2.0"
                    }
                }

            elif method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": "search_stocks",
                            "description": "搜索 A 股公司 by 名称或代码",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "keyword": {"type": "string", "description": "搜索关键词"}
                                },
                                "required": ["keyword"]
                            }
                        },
                        {
                            "name": "get_company_profile",
                            "description": "获取公司档案",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "description": "股票代码，如 600519"}
                                },
                                "required": ["code"]
                            }
                        },
                        {
                            "name": "get_financial_summary",
                            "description": "获取公司财务摘要",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "description": "股票代码"}
                                },
                                "required": ["code"]
                            }
                        },
                        {
                            "name": "generate_report",
                            "description": "生成分析报告 (Markdown)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "description": "股票代码"}
                                },
                                "required": ["code"]
                            }
                        },
                        {
                            "name": "analyze_batch",
                            "description": "批量分析多家公司",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "codes": {"type": "array", "items": {"type": "string"}, "description": "股票代码列表"}
                                },
                                "required": ["codes"]
                            }
                        }
                    ]
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})

                if tool_name == "search_stocks":
                    results = search_stocks(tool_args.get("keyword", ""))
                    content = json.dumps(results, ensure_ascii=False)
                elif tool_name == "get_company_profile":
                    profile = fetch_company(tool_args.get("code", ""))
                    content = json.dumps(profile.to_dict() if profile else {}, ensure_ascii=False, indent=2)
                elif tool_name == "get_financial_summary":
                    summary = self.analyzer.get_financial_summary(tool_args.get("code", ""))
                    content = json.dumps(summary, ensure_ascii=False, indent=2)
                elif tool_name == "generate_report":
                    report = self.analyzer.generate_report(tool_args.get("code", ""))
                    content = report
                elif tool_name == "analyze_batch":
                    results = self.analyzer.analyze_batch(tool_args.get("codes", []))
                    content = json.dumps(results, ensure_ascii=False, indent=2)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

                result = {
                    "content": [{"type": "text", "text": content}]
                }

            else:
                raise ValueError(f"Unknown method: {method}")

            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(e)}
            }


def main():
    """MCP 服务器主循环 - 读取 JSON-RPC 请求，输出 JSON-RPC 响应"""
    server = MCPServer()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = server.handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue


if __name__ == "__main__":
    main()

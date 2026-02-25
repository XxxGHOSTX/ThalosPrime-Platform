// PROPRIETARY AND CONFIDENTIAL
// Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
// This code implements the Thalos Prime Sovereign Discovery Logic.

/**
 * MCP (Model Context Protocol) client for connecting the Concierge Extension
 * to Thalos Prime tool servers without consuming context tokens.
 */

export interface McpTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

export interface McpCallResult {
  content: Array<{ type: string; text: string }>;
  isError?: boolean;
}

export class McpClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async listTools(): Promise<McpTool[]> {
    const response = await fetch(`${this.baseUrl}/tools/list`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    if (!response.ok) {
      throw new Error(`MCP listTools failed: ${response.statusText}`);
    }
    const data = (await response.json()) as { tools: McpTool[] };
    return data.tools;
  }

  async callTool(toolName: string, args: Record<string, unknown>): Promise<McpCallResult> {
    const response = await fetch(`${this.baseUrl}/tools/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: toolName, arguments: args }),
    });
    if (!response.ok) {
      throw new Error(`MCP callTool(${toolName}) failed: ${response.statusText}`);
    }
    return (await response.json()) as McpCallResult;
  }
}

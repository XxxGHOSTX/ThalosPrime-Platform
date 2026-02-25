// PROPRIETARY AND CONFIDENTIAL
// Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
// This code implements the Thalos Prime Sovereign Discovery Logic.

import * as vscode from "vscode";

interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface Session {
  id: string;
  turns: ConversationTurn[];
  seed?: number;
}

/**
 * ConciergeHandler manages multi-turn conversations for the Thalos Prime
 * Concierge Assistant within VS Code / GitHub Copilot Extension.
 */
export class ConciergeHandler {
  private sessions: Map<string, Session> = new Map();

  constructor(private readonly controlPlaneUrl: string) {}

  async createSession(context: Record<string, unknown> = {}): Promise<string> {
    const response = await fetch(`${this.controlPlaneUrl}/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ context }),
    });
    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }
    const data = (await response.json()) as { session_id: string; seed: number };
    const session: Session = { id: data.session_id, turns: [], seed: data.seed };
    this.sessions.set(data.session_id, session);
    return data.session_id;
  }

  async addTurn(sessionId: string, role: "user" | "assistant", content: string): Promise<string> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }
    const turn: ConversationTurn = { role, content, timestamp: new Date().toISOString() };
    session.turns.push(turn);

    const response = await fetch(`${this.controlPlaneUrl}/sessions/${sessionId}/turns`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(turn),
    });
    if (!response.ok) {
      throw new Error(`Failed to add turn: ${response.statusText}`);
    }
    const data = (await response.json()) as { state_hash: string };
    return data.state_hash;
  }

  getSession(sessionId: string): Session | undefined {
    return this.sessions.get(sessionId);
  }

  /**
   * Handle a VS Code chat request from the Concierge participant.
   * Extension point: customize this to route specific commands to agents.
   */
  async handleChatRequest(
    request: vscode.ChatRequest,
    context: vscode.ChatContext,
    stream: vscode.ChatResponseStream,
    token: vscode.CancellationToken
  ): Promise<void> {
    const sessionId = await this.createSession({});
    await this.addTurn(sessionId, "user", request.prompt);

    // Route to specialist agents based on intent
    if (request.prompt.toLowerCase().includes("scan") || request.prompt.toLowerCase().includes("discover")) {
      stream.markdown("🔍 Routing to **@discovery** agent for Shadow AI scan...\n");
    } else if (request.prompt.toLowerCase().includes("fix") || request.prompt.toLowerCase().includes("remediate")) {
      stream.markdown("🔧 Routing to **@remediator** agent for deterministic code fix...\n");
    } else {
      stream.markdown("👋 Welcome to **Thalos Prime Concierge**. How can I assist you?\n");
    }

    await this.addTurn(sessionId, "assistant", "Response dispatched.");
  }
}

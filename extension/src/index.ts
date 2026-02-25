// PROPRIETARY AND CONFIDENTIAL
// Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
// This code implements the Thalos Prime Sovereign Discovery Logic.

import * as vscode from "vscode";
import { ConciergeHandler } from "./concierge_handler";

/**
 * Default Control Plane URL. Override via the THALOS_CONTROL_PLANE_URL
 * environment variable or VS Code settings (thalos.controlPlaneUrl).
 */
const DEFAULT_CONTROL_PLANE_URL = "http://localhost:8000";

/**
 * VS Code extension activation entry point.
 * Registers the Thalos Prime Concierge chat participant.
 */
export function activate(context: vscode.ExtensionContext): void {
  const config = vscode.workspace.getConfiguration("thalos");
  const controlPlaneUrl: string =
    (config.get<string>("controlPlaneUrl") ?? process.env["THALOS_CONTROL_PLANE_URL"]) ||
    DEFAULT_CONTROL_PLANE_URL;

  const handler = new ConciergeHandler(controlPlaneUrl);

  // Register the @concierge chat participant
  const participant = vscode.chat.createChatParticipant(
    "thalos.concierge",
    async (
      request: vscode.ChatRequest,
      chatContext: vscode.ChatContext,
      stream: vscode.ChatResponseStream,
      token: vscode.CancellationToken
    ) => {
      await handler.handleChatRequest(request, chatContext, stream, token);
    }
  );

  participant.iconPath = new vscode.ThemeIcon("shield");
  participant.followupProvider = {
    provideFollowups(
      _result: vscode.ChatResult,
      _context: vscode.ChatContext,
      _token: vscode.CancellationToken
    ): vscode.ChatFollowup[] {
      return [
        { prompt: "Run a Shadow AI scan", label: "🔍 Scan for Shadow AI" },
        { prompt: "Generate a remediation fix", label: "🔧 Remediate finding" },
        { prompt: "Audit this site for Agentic Web readiness", label: "🌐 Agentic Web Audit" },
      ];
    },
  };

  context.subscriptions.push(participant);

  // Register a command to open the STATELOG
  const openStatelogCmd = vscode.commands.registerCommand("thalos.openStatelog", () => {
    const statelogPath = vscode.Uri.joinPath(
      vscode.workspace.workspaceFolders?.[0]?.uri ?? vscode.Uri.file("."),
      "STATELOG",
      "events.jsonl"
    );
    vscode.workspace.openTextDocument(statelogPath).then((doc) => {
      vscode.window.showTextDocument(doc);
    });
  });

  context.subscriptions.push(openStatelogCmd);
}

/**
 * Called when the extension is deactivated.
 */
export function deactivate(): void {
  // Clean up resources if needed
}

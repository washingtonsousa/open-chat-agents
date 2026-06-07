"use client";

import { useEffect, useState } from "react";
import { agentApi, ollamaApi } from "@/services/api";
import type { Agent, AgentCreate, OllamaModel } from "@/types";

interface Props {
  onCreated: (agent: Agent) => void;
  onCancel: () => void;
}

const DEFAULTS: AgentCreate = {
  name: "",
  llm_model: "",
  temperature: 0.7,
  max_tokens: null,
  system_prompt: "Você é um assistente prestativo e amigável.",
};

export function AgentForm({ onCreated, onCancel }: Props) {
  const [form, setForm] = useState<AgentCreate>(DEFAULTS);
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [loadingModels, setLoadingModels] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    ollamaApi
      .listModels()
      .then((res) => {
        setModels(res.models);
        if (res.models.length > 0) setForm((f) => ({ ...f, llm_model: res.models[0].name }));
      })
      .catch(() => setError("Não foi possível listar os modelos do Ollama."))
      .finally(() => setLoadingModels(false));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const agent = await agentApi.create(form);
      onCreated(agent);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar agente.");
    } finally {
      setSubmitting(false);
    }
  }

  function set<K extends keyof AgentCreate>(key: K, value: AgentCreate[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Nome do agente</label>
        <input
          required
          value={form.name}
          onChange={(e) => set("name", e.target.value)}
          placeholder="Ex: Assistente de Vendas"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Modelo LLM</label>
        {loadingModels ? (
          <p className="text-sm text-gray-400">Carregando modelos...</p>
        ) : models.length === 0 ? (
          <p className="text-sm text-red-500">Nenhum modelo encontrado no Ollama.</p>
        ) : (
          <select
            required
            value={form.llm_model}
            onChange={(e) => set("llm_model", e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {models.map((m) => (
              <option key={m.name} value={m.name}>
                {m.name}
              </option>
            ))}
          </select>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Temperatura <span className="text-gray-400">({form.temperature})</span>
          </label>
          <input
            type="range"
            min={0}
            max={2}
            step={0.1}
            value={form.temperature}
            onChange={(e) => set("temperature", parseFloat(e.target.value))}
            className="w-full accent-blue-600"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-0.5">
            <span>Preciso</span>
            <span>Criativo</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Máx. tokens</label>
          <input
            type="number"
            min={1}
            value={form.max_tokens ?? ""}
            onChange={(e) => set("max_tokens", e.target.value ? parseInt(e.target.value) : null)}
            placeholder="Sem limite"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Prompt inicial (system prompt)</label>
        <textarea
          required
          rows={4}
          value={form.system_prompt}
          onChange={(e) => set("system_prompt", e.target.value)}
          placeholder="Defina o comportamento e contexto do agente..."
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <div className="flex justify-end gap-2 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-100 transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={submitting || loadingModels}
          className="px-4 py-2 rounded-lg text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {submitting ? "Criando..." : "Criar agente"}
        </button>
      </div>
    </form>
  );
}

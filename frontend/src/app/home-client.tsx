"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { buildApiUrl } from "@/lib/api";

type HealthPayload = {
  status: string;
  time: string;
  deployment_environment?: string;
};

export default function HomeClient() {
  const [health, setHealth] = useState<HealthPayload | null | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const response = await fetch(buildApiUrl("/api/v1/health"), { cache: "no-store" });
        if (!response.ok) {
          if (!cancelled) setHealth(null);
          return;
        }
        const payload = (await response.json()) as HealthPayload;
        if (!cancelled) setHealth(payload);
      } catch {
        if (!cancelled) setHealth(null);
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="min-h-screen bg-zinc-50 text-zinc-900">
      <div className="mx-auto flex max-w-3xl flex-col gap-10 px-6 py-16">
        <header className="space-y-3">
          <p className="text-sm font-medium text-zinc-500">Squad Five · Capstone scaffold</p>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">TalentStreamAI</h1>
          <p className="text-base leading-relaxed text-zinc-600">
            Static Next.js export behind CloudFront, FastAPI on ECS Fargate behind API Gateway, Aurora
            Serverless v2 with Data API + Secrets Manager, and CI/CD that applies Terraform from GitHub
            Actions using OIDC. LangGraph + OpenRouter live in the container task; Clerk JWT validation
            is enforced at the HTTP API layer (except the public health probe).
          </p>
        </header>

        <section className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-500">API check</h2>
          <div className="mt-4 space-y-2 text-sm">
            {health === undefined ? (
              <p className="text-zinc-600">Checking API…</p>
            ) : health ? (
              <>
                <p className="font-medium text-emerald-700">Backend reachable</p>
                <p className="text-zinc-600">
                  Reported at <span className="font-mono text-xs">{health.time}</span>
                </p>
                {health.deployment_environment ? (
                  <p className="text-zinc-600">
                    Deployment tag{" "}
                    <span className="font-mono text-xs">{health.deployment_environment}</span>
                  </p>
                ) : null}
              </>
            ) : (
              <>
                <p className="font-medium text-amber-700">Backend not responding</p>
                <p className="text-zinc-600">
                  For local Docker use <code className="font-mono text-xs">./scripts/run.sh</code>. For
                  static export, set <code className="font-mono text-xs">NEXT_PUBLIC_API_URL</code> in the
                  repo root <code className="font-mono text-xs">.env</code> during{" "}
                  <code className="font-mono text-xs">npm run build</code>, or leave it empty and serve the
                  site from the same hostname as the API Gateway/CloudFront distribution.
                </p>
              </>
            )}
          </div>
        </section>

        <section className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-zinc-200 bg-white p-5">
            <h3 className="text-sm font-semibold text-zinc-900">Where to work</h3>
            <ul className="mt-3 space-y-2 text-sm text-zinc-600">
              <li>
                <span className="font-mono text-xs text-zinc-800">backend/app</span> for FastAPI routes,
                LangGraph agents, and Data API calls
              </li>
              <li>
                <span className="font-mono text-xs text-zinc-800">frontend/src</span> for UI flows
              </li>
              <li>
                <span className="font-mono text-xs text-zinc-800">terraform</span> for the single-stack AWS
                deployment
              </li>
            </ul>
          </div>
          <div className="rounded-xl border border-zinc-200 bg-white p-5">
            <h3 className="text-sm font-semibold text-zinc-900">Handy links</h3>
            <ul className="mt-3 space-y-2 text-sm text-zinc-600">
              <li>
                <Link className="text-blue-700 underline-offset-4 hover:underline" href="/">
                  Home
                </Link>{" "}
                (you are here)
              </li>
              <li>
                <span className="text-zinc-600">
                  OpenAPI docs are served from the API service (local:{" "}
                  <a
                    className="text-blue-700 underline-offset-4 hover:underline"
                    href="http://localhost:8000/docs"
                    rel="noreferrer"
                    target="_blank"
                  >
                    /docs
                  </a>
                  ).
                </span>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </main>
  );
}

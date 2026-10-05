import { useEffect, useState, type FormEvent } from "react";
import { createHook, fetchAssets, fetchHooks, fetchIntegrations, updateIntegration } from "../api/marketing";
import type { ChannelIntegration, ContentAsset, MarketingHook } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { Badge, PageHeader, Panel, SampleNote, toneFor } from "../components/ui";
import { sampleAssets, sampleHooks, sampleIntegrations } from "../data/samples";
import { titleCase } from "../lib/format";

export default function MarketingPage() {
  const { preview } = useAuth();
  const [assets, setAssets] = useState<ContentAsset[]>(sampleAssets);
  const [hooks, setHooks] = useState<MarketingHook[]>(sampleHooks);
  const [channels, setChannels] = useState<ChannelIntegration[]>(sampleIntegrations);
  const [illustrative, setIllustrative] = useState(true);
  const [headline, setHeadline] = useState("");
  const [platform, setPlatform] = useState("instagram");

  useEffect(() => {
    if (preview) {
      setAssets(sampleAssets);
      setHooks(sampleHooks);
      setChannels(sampleIntegrations);
      setIllustrative(true);
      return;
    }
    let cancelled = false;
    void Promise.all([fetchAssets(), fetchHooks(), fetchIntegrations()])
      .then(([liveAssets, liveHooks, liveChannels]) => {
        if (cancelled) return;
        const empty = liveAssets.length + liveHooks.length + liveChannels.length === 0;
        setAssets(liveAssets.length ? liveAssets : sampleAssets);
        setHooks(liveHooks.length ? liveHooks : sampleHooks);
        setChannels(liveChannels.length ? liveChannels : sampleIntegrations);
        setIllustrative(empty);
      })
      .catch(() => {
        if (!cancelled) setIllustrative(true);
      });
    return () => {
      cancelled = true;
    };
  }, [preview]);

  async function addHook(event: FormEvent) {
    event.preventDefault();
    const draft: MarketingHook = {
      id: `local-${Date.now()}`,
      headline,
      angle: "routine",
      platform,
      status: "draft",
    };
    setHooks((current) => [draft, ...current]);
    setHeadline("");
    if (illustrative || preview) return;
    try {
      const saved = await createHook({ headline: draft.headline, angle: draft.angle, platform: draft.platform });
      setHooks((current) => current.map((hook) => (hook.id === draft.id ? saved : hook)));
    } catch {
      setHooks((current) => current.filter((hook) => hook.id !== draft.id));
    }
  }

  async function toggleChannel(channel: ChannelIntegration) {
    const status = channel.status === "connected" ? "disconnected" : "connected";
    setChannels((current) => current.map((row) => (row.id === channel.id ? { ...row, status } : row)));
    if (illustrative || preview) return;
    try {
      await updateIntegration(channel.id, { status });
    } catch {
      setChannels((current) => current.map((row) => (row.id === channel.id ? channel : row)));
    }
  }

  return (
    <div>
      <PageHeader
        desk="Growth desk"
        title="Marketing"
        lede="Creative the store can run, hooks ready for a post, and the social and ads accounts sitting beside the brand."
      />
      <SampleNote show={illustrative} />
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel>
          <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">Assets</p>
          <ul className="mt-4 space-y-4">
            {assets.map((asset) => (
              <li key={asset.id}>
                <div className="flex items-center justify-between gap-3">
                  <p>{asset.title}</p>
                  <Badge tone={toneFor(asset.status)}>{titleCase(asset.status)}</Badge>
                </div>
                <p className="mt-1 text-sm text-ink-soft">{titleCase(asset.kind)} · {titleCase(asset.channel)}</p>
                <p className="mt-2 text-sm leading-6">{asset.body}</p>
              </li>
            ))}
          </ul>
        </Panel>
        <Panel>
          <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">Hooks</p>
          <ul className="mt-4 space-y-4">
            {hooks.map((hook) => (
              <li key={hook.id} className="border-b border-line pb-4 last:border-0">
                <p className="font-display text-2xl leading-snug">{hook.headline}</p>
                <p className="mt-2 text-xs uppercase tracking-[0.16em] text-ink-soft">{titleCase(hook.platform)} · {titleCase(hook.angle)} · {titleCase(hook.status)}</p>
              </li>
            ))}
          </ul>
          <form onSubmit={addHook} className="mt-4 flex flex-col gap-2 sm:flex-row">
            <input
              className="min-w-0 flex-1 rounded-2xl border border-line bg-paper px-3 py-2 text-sm"
              placeholder="A new line for the feed"
              value={headline}
              onChange={(event) => setHeadline(event.target.value)}
              required
            />
            <select className="rounded-2xl border border-line bg-paper px-3 py-2 text-sm" value={platform} onChange={(event) => setPlatform(event.target.value)}>
              <option value="instagram">Instagram</option>
              <option value="tiktok">TikTok</option>
              <option value="email">Email</option>
            </select>
            <button className="rounded-full bg-ink px-4 py-2 text-sm text-cream" type="submit">Add</button>
          </form>
        </Panel>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {channels.map((channel) => (
          <Panel key={channel.id}>
            <div className="flex items-center justify-between">
              <p>{titleCase(channel.provider)}</p>
              <Badge tone={toneFor(channel.status)}>{titleCase(channel.status)}</Badge>
            </div>
            <p className="mt-2 min-h-5 text-sm text-ink-soft">{channel.account_label || "No account label yet"}</p>
            <button className="mt-4 text-sm underline" type="button" onClick={() => void toggleChannel(channel)}>
              {channel.status === "connected" ? "Disconnect" : "Mark connected"}
            </button>
          </Panel>
        ))}
      </div>
    </div>
  );
}

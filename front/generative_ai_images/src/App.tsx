import { useState } from "react";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [images, setImages] = useState({ base: null, trained: null });
  const [loading, setLoading] = useState(false);

  // Trained model parameters
  const [trainedParams, setTrainedParams] = useState({
    negative_prompt: "",
    steps: 30,
    cfg_scale: 7,
    seed: -1,
    sampler: "DPM++ 2M",
    width: 512,
    height: 512,
    lora_scale: 1.0,
  });

  const updateParam = (key: string, value: any) => {
    setTrainedParams((prev) => ({ ...prev, [key]: value }));
  };

  const generateImages = async () => {
    if (!prompt) return;

    setLoading(true);
    setImages({ base: null, trained: null });

    try {
      const payloadBase = { prompt };
      const payloadTrained = { prompt, ...trainedParams };

      const [baseRes, trainedRes] = await Promise.all([
        fetch("/api/generate/base", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payloadBase),
        }),
        fetch("/api/generate/trained", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payloadTrained),
        }),
      ]);

      const baseData = await baseRes.json();
      const trainedData = await trainedRes.json();

      setImages({
        base: baseData.image,
        trained: trainedData.image,
      });
    } catch (err) {
      alert("Image generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">

        {/* LEFT PANEL */}
        <div className="bg-slate-800/70 backdrop-blur rounded-2xl p-6 shadow-xl space-y-5 overflow-y-auto max-h-screen">
          <h1 className="text-3xl font-bold">AI Image Comparison</h1>

          <textarea
            className="w-full rounded-xl bg-slate-900 border border-slate-700 p-4 focus:outline-none focus:ring focus:ring-indigo-500"
            rows={4}
            placeholder="Describe the image you want..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />

          {/* TRAINED MODEL CONTROLS */}
          <div className="space-y-4 border-t border-slate-700 pt-4">
            <h2 className="text-lg font-semibold">Trained Model Parameters</h2>

            <input
              className="w-full rounded-lg bg-slate-900 border border-slate-700 p-2"
              placeholder="Negative prompt"
              value={trainedParams.negative_prompt}
              onChange={(e) => updateParam("negative_prompt", e.target.value)}
            />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm">Steps: {trainedParams.steps}</label>
                <input
                  title="Steps"
                  type="range"
                  min="10"
                  max="80"
                  value={trainedParams.steps}
                  onChange={(e) => updateParam("steps", Number(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="text-sm">CFG Scale: {trainedParams.cfg_scale}</label>
                <input
                  title="CFG Scale"
                  type="range"
                  min="1"
                  max="20"
                  step="0.5"
                  value={trainedParams.cfg_scale}
                  onChange={(e) => updateParam("cfg_scale", Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <input
                type="number"
                className="rounded-lg bg-slate-900 border border-slate-700 p-2"
                placeholder="Seed (-1 = random)"
                title="Seed (-1 = random)"
                value={trainedParams.seed}
                onChange={(e) => updateParam("seed", Number(e.target.value))}
              />

              <select
                title="Sampler"
                className="rounded-lg bg-slate-900 border border-slate-700 p-2"
                value={trainedParams.sampler}
                onChange={(e) => updateParam("sampler", e.target.value)}
              >
                <option>DPM++ 2M</option>
                <option>Euler</option>
                <option>Euler a</option>
                <option>DDIM</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm">Width</label>
                <input
                title="Width"
                  type="number"
                  className="w-full rounded-lg bg-slate-900 border border-slate-700 p-2"
                  value={trainedParams.width}
                  onChange={(e) => updateParam("width", Number(e.target.value))}
                />
              </div>
              <div>
                <label className="text-sm">Height</label>
                <input
                  title="Height"
                  type="number"
                  className="w-full rounded-lg bg-slate-900 border border-slate-700 p-2"
                  value={trainedParams.height}
                  onChange={(e) => updateParam("height", Number(e.target.value))}
                />
              </div>
            </div>

            <div>
              <label className="text-sm">LoRA Scale: {trainedParams.lora_scale}</label>
              <input
                title="Lora Scale"
                type="range"
                min="0"
                max="2"
                step="0.05"
                value={trainedParams.lora_scale}
                onChange={(e) => updateParam("lora_scale", Number(e.target.value))}
                className="w-full"
              />
            </div>
          </div>

          <button
            onClick={generateImages}
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 transition py-3 rounded-xl font-semibold"
          >
            {loading ? "Generating…" : "Generate Images"}
          </button>
        </div>

        {/* RIGHT PANEL */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex flex-col items-center justify-center bg-slate-800/40 rounded-2xl shadow-inner p-4">
            <h2 className="mb-3 font-semibold">Base Stable Diffusion</h2>
            {images.base ? (
              <img src={images.base} alt="base model" className="rounded-xl max-h-[500px] object-contain" />
            ) : (
              <p className="text-slate-400">Waiting for generation</p>
            )}
          </div>

          <div className="flex flex-col items-center justify-center bg-slate-800/40 rounded-2xl shadow-inner p-4">
            <h2 className="mb-3 font-semibold">Trained Model</h2>
            {images.trained ? (
              <img src={images.trained} alt="trained model" className="rounded-xl max-h-[500px] object-contain" />
            ) : (
              <p className="text-slate-400">Waiting for generation</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
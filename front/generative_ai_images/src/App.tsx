import { useState } from "react";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [images, setImages] = useState<{ base: Blob | null; trained: Blob | null }>({ base: null, trained: null });
  const [loading, setLoading] = useState(false);

  const endpointBaseModel = "/api/ai/baseModel";
  const endpointTrainedModel = "/api/ai/trainedModel";

  // LoRA-trained model parameters (Diffusers-compatible)
  const [trainedParams, setTrainedParams] = useState({
    negative_prompt: "",
    steps: 30,
    cfg_scale: 7.5,
    seed: -1, // -1 = random
    width: 512,
    height: 512,
    lora_scale: 1.0,
  });

  const updateParam = (key: string, value: unknown) => {
    setTrainedParams((prev) => ({ ...prev, [key]: value }));
  };

  const generateImages = async () => {
    if (!prompt) return;

    setLoading(true);
    setImages({ base: null, trained: null });

    try {
      const payloadBase = { prompt };

      const payloadTrained = {
        prompt,
        negative_prompt: trainedParams.negative_prompt,
        num_inference_steps: trainedParams.steps,
        guidance_scale: trainedParams.cfg_scale,
        seed: trainedParams.seed,
        width: trainedParams.width,
        height: trainedParams.height,
        lora_scale: trainedParams.lora_scale,
      };

      const [baseRes, trainedRes] = await Promise.all([
        fetch(endpointBaseModel, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payloadBase),
        }),
        fetch(endpointTrainedModel, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payloadTrained),
        }),
      ]);

      const baseBlob = await baseRes.blob();
      const traineBlob = await trainedRes.blob();

      setImages({
        base: baseBlob,
        trained: traineBlob,
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
          <h1 className="text-3xl font-bold">LoRA Image Comparison</h1>

          <textarea
            className="w-full rounded-xl bg-slate-900 border border-slate-700 p-4"
            rows={4}
            placeholder="Describe the image you want..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />

          {/* TRAINED MODEL PARAMETERS */}
          <div className="space-y-4 border-t border-slate-700 pt-4">
            <h2 className="text-lg font-semibold">LoRA Parameters</h2>

            <input
              className="w-full rounded-lg bg-slate-900 border border-slate-700 p-2"
              placeholder="Negative prompt"
              value={trainedParams.negative_prompt}
              onChange={(e) => updateParam("negative_prompt", e.target.value)}
            />

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

            <div className="grid grid-cols-2 gap-4">
              <label className="text-sm col-span-2">Seed and LoRA Scale</label>
              <input
                type="number"
                className="rounded-lg bg-slate-900 border border-slate-700 p-2"
                placeholder="Seed (-1 = random)"
                value={trainedParams.seed}
                onChange={(e) => updateParam("seed", Number(e.target.value))}
              />
              <input
                type="number"
                className="rounded-lg bg-slate-900 border border-slate-700 p-2"
                placeholder="LoRA scale"
                step="0.05"
                value={trainedParams.lora_scale}
                onChange={(e) => updateParam("lora_scale", Number(e.target.value))}
              />
            </div>
            <label className="text-sm">Image Dimensions</label>
            <div className="grid grid-cols-2 gap-4">
              <input
                type="number"
                className="rounded-lg bg-slate-900 border border-slate-700 p-2"
                placeholder="Width"
                value={trainedParams.width}
                onChange={(e) => updateParam("width", Number(e.target.value))}
              />
              <input
                type="number"
                className="rounded-lg bg-slate-900 border border-slate-700 p-2"
                placeholder="Height"
                value={trainedParams.height}
                onChange={(e) => updateParam("height", Number(e.target.value))}
              />
            </div>
          </div>

          <button
            onClick={generateImages}
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 py-3 rounded-xl font-semibold"
          >
            {loading ? "Generating…" : "Generate Images"}
          </button>
        </div>

        {/* RIGHT PANEL */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-800/40 rounded-2xl p-4 text-center">
            <h2 className="mb-3 font-semibold">Base SD</h2>
            {images.base ? <img title="BASESD" src={URL.createObjectURL(images.base)} className="rounded-xl mx-auto" /> : "Waiting"}
          </div>

          <div className="bg-slate-800/40 rounded-2xl p-4 text-center">
            <h2 className="mb-3 font-semibold">LoRA Model</h2>
            {images.trained ? <img title="LORA MODEL" src={URL.createObjectURL(images.trained)} className="rounded-xl mx-auto" /> : "Waiting"}
          </div>
        </div>

      </div>
    </div>
  );
}

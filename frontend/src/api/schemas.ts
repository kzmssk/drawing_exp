// backend の pydantic 応答スキーマに 1:1 対応する zod スキーマと型。

import { z } from 'zod'

export const artifactKindSchema = z.enum(['image', 'video', 'json', 'other'])

export const runMetricsSchema = z.object({
  n_steps: z.number(),
  duration_s: z.number(),
  coverage: z.number(),
  pen_path_len_m: z.number(),
  stable: z.boolean(),
})

export const artifactInfoSchema = z.object({
  name: z.string(),
  kind: artifactKindSchema,
  url: z.string(),
  size_bytes: z.number(),
})

export const runSummarySchema = z.object({
  experiment: z.string(),
  run_id: z.string(),
  created_at: z.string(),
  metrics: runMetricsSchema.nullable(),
  artifact_count: z.number(),
  thumbnail_url: z.string().nullable(),
})

export const runDetailSchema = z.object({
  experiment: z.string(),
  run_id: z.string(),
  created_at: z.string(),
  metrics: runMetricsSchema.nullable(),
  config: z.record(z.string(), z.unknown()).nullable(),
  artifacts: z.array(artifactInfoSchema),
})

export const runSummaryListSchema = z.array(runSummarySchema)

export type ArtifactKind = z.infer<typeof artifactKindSchema>
export type RunMetrics = z.infer<typeof runMetricsSchema>
export type ArtifactInfo = z.infer<typeof artifactInfoSchema>
export type RunSummary = z.infer<typeof runSummarySchema>
export type RunDetail = z.infer<typeof runDetailSchema>

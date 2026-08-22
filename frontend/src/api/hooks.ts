// run 一覧・詳細を取得する react-query フック(取得後に zod で検証)。

import { useQuery } from '@tanstack/react-query'
import { getJson } from './client'
import { runDetailSchema, runSummaryListSchema } from './schemas'

export function useRuns(experiment?: string) {
  return useQuery({
    queryKey: ['runs', experiment ?? null],
    queryFn: async () => {
      const q = experiment ? `?experiment=${encodeURIComponent(experiment)}` : ''
      return runSummaryListSchema.parse(await getJson(`/runs${q}`))
    },
  })
}

export function useRun(experiment: string, runId: string) {
  return useQuery({
    queryKey: ['run', experiment, runId],
    queryFn: async () =>
      runDetailSchema.parse(
        await getJson(
          `/runs/${encodeURIComponent(experiment)}/${encodeURIComponent(runId)}`,
        ),
      ),
  })
}

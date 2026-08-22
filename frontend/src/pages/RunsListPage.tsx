// run 一覧ページ。実験名で絞り込み、行から詳細へ遷移する。

import { useMemo, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import {
  Alert,
  Box,
  Card,
  CardActionArea,
  CardContent,
  CircularProgress,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useRuns } from '../api/hooks'

export function RunsListPage() {
  const [experiment, setExperiment] = useState('')
  const navigate = useNavigate()
  const { data, isLoading, error } = useRuns()

  const experiments = useMemo(() => {
    const names = new Set((data ?? []).map((r) => r.experiment))
    return Array.from(names).sort()
  }, [data])

  const runs = (data ?? []).filter(
    (r) => experiment === '' || r.experiment === experiment,
  )

  if (isLoading) return <CircularProgress />
  if (error) return <Alert severity="error">{String(error)}</Alert>

  return (
    <Stack spacing={2}>
      <TextField
        select
        label="実験で絞り込み"
        value={experiment}
        onChange={(e) => setExperiment(e.target.value)}
        sx={{ maxWidth: 280 }}
        size="small"
      >
        <MenuItem value="">すべて</MenuItem>
        {experiments.map((name) => (
          <MenuItem key={name} value={name}>
            {name}
          </MenuItem>
        ))}
      </TextField>

      {runs.length === 0 && <Typography>run がありません。</Typography>}

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
          gap: 2,
        }}
      >
        {runs.map((r) => (
          <Card key={`${r.experiment}/${r.run_id}`} variant="outlined">
            <CardActionArea
              onClick={() =>
                navigate({
                  to: '/runs/$experiment/$runId',
                  params: { experiment: r.experiment, runId: r.run_id },
                })
              }
            >
              {r.thumbnail_url && (
                <Box
                  component="img"
                  src={r.thumbnail_url}
                  alt=""
                  sx={{
                    width: '100%',
                    aspectRatio: '1 / 1',
                    objectFit: 'contain',
                    bgcolor: '#fff',
                    imageRendering: 'pixelated',
                  }}
                />
              )}
              <CardContent>
                <Typography variant="subtitle1">{r.experiment}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {r.run_id}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(r.created_at).toLocaleString()}
                </Typography>
                {r.metrics && (
                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                    被覆率 {(r.metrics.coverage * 100).toFixed(1)}%
                  </Typography>
                )}
              </CardContent>
            </CardActionArea>
          </Card>
        ))}
      </Box>
    </Stack>
  )
}

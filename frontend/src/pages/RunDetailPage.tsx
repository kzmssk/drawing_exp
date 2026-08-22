// run 詳細ページ。成果物(画像・動画)と metrics・config を表示する。

import { Link as RouterLink, useParams } from '@tanstack/react-router'
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Stack,
  Typography,
} from '@mui/material'
import { useRun } from '../api/hooks'
import { ArtifactView } from '../components/ArtifactView'

export function RunDetailPage() {
  const { experiment, runId } = useParams({ from: '/runs/$experiment/$runId' })
  const { data, isLoading, error } = useRun(experiment, runId)

  if (isLoading) return <CircularProgress />
  if (error) return <Alert severity="error">{String(error)}</Alert>
  if (!data) return <Alert severity="warning">run が見つかりません。</Alert>

  const media = data.artifacts.filter(
    (a) => a.kind === 'image' || a.kind === 'video',
  )
  const others = data.artifacts.filter(
    (a) => a.kind !== 'image' && a.kind !== 'video',
  )

  return (
    <Stack spacing={2}>
      <Button
        component={RouterLink}
        to="/"
        variant="text"
        sx={{ alignSelf: 'flex-start' }}
      >
        ← 一覧へ
      </Button>

      <Box>
        <Typography variant="h6">
          {data.experiment} / {data.run_id}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {new Date(data.created_at).toLocaleString()}
        </Typography>
      </Box>

      {data.metrics && (
        <Stack direction="row" spacing={1} useFlexGap sx={{ flexWrap: 'wrap' }}>
          <Chip label={`ステップ ${data.metrics.n_steps}`} />
          <Chip label={`${data.metrics.duration_s}s`} />
          <Chip label={`被覆率 ${(data.metrics.coverage * 100).toFixed(1)}%`} />
          <Chip label={`移動 ${data.metrics.pen_path_len_m.toFixed(2)}m`} />
          <Chip
            label={data.metrics.stable ? '安定' : '不安定'}
            color={data.metrics.stable ? 'success' : 'error'}
          />
        </Stack>
      )}

      <Divider />

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: 3,
        }}
      >
        {media.map((a) => (
          <ArtifactView key={a.name} artifact={a} />
        ))}
      </Box>

      {others.length > 0 && (
        <Stack spacing={1}>
          {others.map((a) => (
            <ArtifactView key={a.name} artifact={a} />
          ))}
        </Stack>
      )}

      {data.config && (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            config
          </Typography>
          <Paper
            variant="outlined"
            component="pre"
            sx={{
              p: 2,
              m: 0,
              overflowX: 'auto',
              fontSize: 13,
              fontFamily: 'monospace',
            }}
          >
            {JSON.stringify(data.config, null, 2)}
          </Paper>
        </Box>
      )}
    </Stack>
  )
}

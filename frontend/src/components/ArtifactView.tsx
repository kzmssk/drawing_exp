// 成果物を種別に応じて描画する(画像/動画/その他リンク)。

import { Box, Link, Typography } from '@mui/material'
import type { ArtifactInfo } from '../api/schemas'

export function ArtifactView({ artifact }: { artifact: ArtifactInfo }) {
  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        {artifact.name}
      </Typography>
      {artifact.kind === 'image' && (
        <Box
          component="img"
          src={artifact.url}
          alt={artifact.name}
          sx={{
            width: '100%',
            maxWidth: 360,
            imageRendering: 'pixelated',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
          }}
        />
      )}
      {artifact.kind === 'video' && (
        <Box
          component="video"
          src={artifact.url}
          controls
          loop
          sx={{ width: '100%', maxWidth: 512, borderRadius: 1, display: 'block' }}
        />
      )}
      {(artifact.kind === 'json' || artifact.kind === 'other') && (
        <Link href={artifact.url} target="_blank" rel="noreferrer">
          開く ({(artifact.size_bytes / 1024).toFixed(1)} KB)
        </Link>
      )}
    </Box>
  )
}

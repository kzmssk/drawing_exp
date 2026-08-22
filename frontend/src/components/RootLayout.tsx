// 全ページ共通レイアウト(ヘッダ + Outlet)。

import { Link as RouterLink, Outlet } from '@tanstack/react-router'
import { AppBar, Box, Container, Toolbar, Typography } from '@mui/material'

export function RootLayout() {
  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{ color: 'inherit', textDecoration: 'none' }}
          >
            drawing-exp 実験結果ビューア
          </Typography>
        </Toolbar>
      </AppBar>
      <Container sx={{ py: 3 }}>
        <Outlet />
      </Container>
    </Box>
  )
}

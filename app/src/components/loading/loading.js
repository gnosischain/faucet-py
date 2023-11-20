import Backdrop from "@mui/material/Backdrop";
import { Box, CircularProgress } from "@mui/material";

export default function Loading(props) {
  const { open } = props;

  return (
    <Backdrop
      sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
      open={open}
    >
      <Box sx={{ display: "flex" }}>
        <CircularProgress />
      </Box>
    </Backdrop>
  );
}

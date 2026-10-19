import { createBrowserRouter } from "react-router";
import { Root } from "./components/Root";
import { Home } from "./components/Home";
import { ProfileInput } from "./components/ProfileInput";
import { Result } from "./components/Result";
import { History } from "./components/History";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "profile", Component: ProfileInput },
      { path: "result", Component: Result },
      { path: "history", Component: History },
    ],
  },
]);

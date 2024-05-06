import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import {SendersPage} from "./pages/SendersPage.tsx";
import TimeAgo from 'javascript-time-ago'

import en from 'javascript-time-ago/locale/en'

TimeAgo.addDefaultLocale(en)

import {
    createHashRouter,
    RouterProvider,
} from "react-router-dom";
import {
    QueryClient,
    QueryClientProvider,
} from '@tanstack/react-query'
import {MessagesPage} from "./pages/MessagesPage.tsx";

const router = createHashRouter([
    {
        path: "/",
        element: <App />,
        children: [
            {
                path: "senders",
                element: <SendersPage />
            },
            {
                path: "senders/:senderId",
                element: <MessagesPage />
            },
            {
                path: "messages",
                element: <MessagesPage />
            }
        ]
    },
]);

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router}/>
      </QueryClientProvider>
  </React.StrictMode>,
)

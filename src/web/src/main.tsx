import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { Auth0Provider } from '@auth0/auth0-react';


let auth0_domain = "emlab.uk.auth0.com";
let auth0_client_id = "3Dl2QwlW35gS8oQ6xXiG0nzCyy1g1GAq";

if (window.location.hostname === 'localhost') {
    auth0_domain = "dev-emlab.uk.auth0.com";
    auth0_client_id = "Z1G5QBaAQWuVS2OtJ9NgCFCpFCtZ8U7Z";
}

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <Auth0Provider
            domain={auth0_domain}
            clientId={auth0_client_id}
            authorizationParams={{
                redirect_uri: window.location.origin,
                audience: "https://emlab.ai/api/",
                scope: "openid profile email"
            }}
        >
            <App />
        </Auth0Provider>
    </React.StrictMode>
)

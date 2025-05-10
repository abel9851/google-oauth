<template>
  <div class="login-container">
    <h2>Sign in to continue</h2>
    <div id="google-signin-btn" ref="googleButton"></div>
    <div class="server-auth">
      <button @click="loginWithServer" class="server-auth-btn">
        Sign in with Google (Server Flow)
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "LoginButton",
  data() {
    return {
      scriptLoaded: false,
      buttonRendered: false,
    };
  },
  mounted() {
    // Load the Google Identity Services script
    if (!this.scriptLoaded) {
      const script = document.createElement("script");
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = this.initializeGoogleButton;
      document.head.appendChild(script);
      this.scriptLoaded = true;
    } else {
      this.initializeGoogleButton();
    }
  },
  methods: {
    // Initialize Google Sign-In button
    initializeGoogleButton() {
      if (window.google && !this.buttonRendered) {
        // Client-side auth (not used in our server-side flow)
        // Kept for demonstration of both auth flows
        window.google.accounts.id.initialize({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
          callback: this.handleCredentialResponse,
          auto_select: false,
          cancel_on_tap_outside: true,
        });
        
        // Render the button
        window.google.accounts.id.renderButton(
          this.$refs.googleButton,
          {
            theme: "outline", 
            size: "large",
            type: "standard",
            text: "signin_with",
            shape: "rectangular",
            logo_alignment: "left",
            width: 280,
          }
        );
        
        this.buttonRendered = true;
      }
    },
    
    // Handle credentials from client-side flow (not used in our primary flow)
    handleCredentialResponse(response) {
      console.log("Credential response:", response);
      // In our app, we use server-side flow instead
    },
    
    // Redirect to backend authorize endpoint
    loginWithServer() {
      window.location.href = `${import.meta.env.VITE_API_URL}/oauth/authorize`;
    }
  }
};
</script>

<style scoped>
.login-container {
  max-width: 320px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  border: 1px solid #eaeaea;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

h2 {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
}

.server-auth {
  margin-top: 1rem;
  width: 100%;
}

.server-auth-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #fff;
  color: #444;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, box-shadow 0.2s;
}

.server-auth-btn:hover {
  background-color: #f8f8f8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.server-auth-btn:active {
  background-color: #eee;
}
</style> 
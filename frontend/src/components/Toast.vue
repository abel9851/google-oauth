<template>
  <transition name="toast">
    <div v-if="visible" :class="['toast', `toast-${type}`]">
      <div class="toast-content">
        <span class="toast-icon" v-if="type === 'success'">✓</span>
        <span class="toast-icon" v-else-if="type === 'error'">✗</span>
        <span class="toast-icon" v-else-if="type === 'info'">ℹ</span>
        <span class="toast-message">{{ message }}</span>
      </div>
      <button @click="close" class="toast-close">&times;</button>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'ToastNotification',
  props: {
    message: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['success', 'error', 'info'].includes(value)
    },
    duration: {
      type: Number,
      default: 3000
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  watch: {
    visible(newVal) {
      if (newVal && this.duration > 0) {
        setTimeout(() => {
          this.$emit('close');
        }, this.duration);
      }
    }
  },
  methods: {
    close() {
      this.$emit('close');
    }
  }
};
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  min-width: 250px;
  max-width: 350px;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toast-icon {
  font-size: 18px;
  font-weight: bold;
}

.toast-message {
  word-break: break-word;
}

.toast-close {
  background: transparent;
  border: none;
  color: inherit;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.7;
  margin-left: 10px;
}

.toast-close:hover {
  opacity: 1;
}

.toast-success {
  background-color: #d4edda;
  color: #155724;
  border-left: 4px solid #28a745;
}

.toast-error {
  background-color: #f8d7da;
  color: #721c24;
  border-left: 4px solid #dc3545;
}

.toast-info {
  background-color: #cce5ff;
  color: #004085;
  border-left: 4px solid #0d6efd;
}

/* 애니메이션 효과 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 
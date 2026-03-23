/**
 * Simple toast notification module
 */

export class Toast {
  constructor(public message: string, public type: 'success' | 'error' | 'warning' | 'info' = 'success') {}

  show() {
    console.log(`[TOAST - ${this.type.toUpperCase()}] ${this.message}`);
    // You can replace this with actual DOM manipulation if needed
    // or keep it simple if Alpine.js is handling it via events
    const event = new CustomEvent('toast', { detail: { message: this.message, type: this.type }});
    window.dispatchEvent(event);
  }
}

export function createToast(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') {
  const toast = new Toast(message, type);
  toast.show();
  return toast;
}
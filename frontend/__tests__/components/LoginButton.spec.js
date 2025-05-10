import { mount, shallowMount } from '@vue/test-utils';
import LoginButton from '../../src/components/LoginButton.vue';

// window.google 모킹
global.google = {
  accounts: {
    id: {
      initialize: jest.fn(),
      renderButton: jest.fn(),
    },
  },
};

describe('LoginButton.vue', () => {
  beforeEach(() => {
    // 스크립트 로딩 모킹
    document.createElement = jest.fn().mockImplementation((tag) => {
      const element = {
        src: '',
        async: false,
        defer: false,
        onload: () => {},
      };
      if (element.onload) setTimeout(element.onload, 10);
      return element;
    });
    
    document.head.appendChild = jest.fn();
  });

  it('renders the sign in button', () => {
    const wrapper = shallowMount(LoginButton);
    expect(wrapper.text()).toContain('Sign in with Google');
  });

  it('loads Google script on mount', async () => {
    const wrapper = mount(LoginButton);
    await new Promise(resolve => setTimeout(resolve, 20));
    expect(document.createElement).toHaveBeenCalledWith('script');
    expect(document.head.appendChild).toHaveBeenCalled();
  });

  it('redirects to correct URL on server login', () => {
    // window.location.href 모킹
    const originalLocation = window.location;
    delete window.location;
    window.location = { href: jest.fn() };
    
    const apiUrl = 'http://test-api';
    // 환경 변수 모킹
    process.env = {
      ...process.env,
      VITE_API_URL: apiUrl
    };
    
    const wrapper = shallowMount(LoginButton);
    wrapper.find('.server-auth-btn').trigger('click');
    
    expect(window.location.href).toHaveBeenCalledWith(`${apiUrl}/oauth/authorize`);
    
    // 정리
    window.location = originalLocation;
  });
}); 
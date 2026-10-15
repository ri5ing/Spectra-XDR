import { create } from 'zustand';

export interface CopilotMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  model?: string;
  timestamp?: string;
}

interface CopilotContext {
  title?: string;
  sourceType?: 'event' | 'alert' | 'agent' | 'mitre' | 'risk' | 'swarm' | 'database' | 'page';
  data?: any;
  summaryText?: string;
}

interface CopilotStoreState {
  isOpen: boolean;
  messages: CopilotMessage[];
  suggestedQuestions: string[];
  activeContext: CopilotContext | null;
  openCopilot: (context?: CopilotContext, initialQuestion?: string) => void;
  closeCopilot: () => void;
  toggleCopilot: () => void;
  setSuggestedQuestions: (questions: string[]) => void;
  addMessage: (msg: CopilotMessage) => void;
  clearMessages: () => void;
}

export const useCopilotStore = create<CopilotStoreState>((set, get) => ({
  isOpen: false,
  messages: [
    {
      id: 'welcome-1',
      sender: 'ai',
      text: 'Hello Analyst! I am SPECTRA-AI, your Autonomous SOC Cyber Copilot. Ask me anything about any alert, rule, endpoint, MITRE technique, or database record on this screen.',
      model: 'SPECTRA-AI'
    }
  ],
  suggestedQuestions: [
    'Explain the active threats on this system',
    'What containment playbooks should I execute?',
    'Show suspicious outbound C2 network sockets',
    'How do I isolate an infected endpoint?'
  ],
  activeContext: null,

  openCopilot: (context, initialQuestion) => {
    const currentQuestions = context?.sourceType === 'alert' || context?.sourceType === 'event'
      ? [
          'What is the MITRE ATT&CK technique for this activity?',
          'Is this normal system noise or a true security incident?',
          'What are the recommended containment steps?',
          'Explain the raw evidence fields'
        ]
      : context?.sourceType === 'agent'
      ? [
          'Is this endpoint healthy and communicating with Wazuh?',
          'What active processes are currently monitored on this host?',
          'Execute Host Network Quarantine on this agent'
        ]
      : context?.sourceType === 'database'
      ? [
          'What data is stored in this database table?',
          'How is telemetry retained across PostgreSQL and OpenSearch?',
          'Are there any orphaned security records?'
        ]
      : [
          'Summarize the current SOC security posture',
          'What containment actions are pending approval?',
          'Explain the AI model routing policy'
        ];

    set({
      isOpen: true,
      activeContext: context || null,
      suggestedQuestions: currentQuestions
    });

    if (context?.summaryText) {
      const introMsg: CopilotMessage = {
        id: `ctx-${Date.now()}`,
        sender: 'ai',
        text: `Context Loaded: [${context.title || 'Selected Telemetry Item'}]\n${context.summaryText}\n\nHow can I assist with your investigation?`,
        model: 'SPECTRA-AI'
      };
      set((state) => ({ messages: [...state.messages, introMsg] }));
    }
  },

  closeCopilot: () => set({ isOpen: false }),
  toggleCopilot: () => set((state) => ({ isOpen: !state.isOpen })),
  setSuggestedQuestions: (questions) => set({ suggestedQuestions: questions }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  clearMessages: () => set({ messages: [] })
}));

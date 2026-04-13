export interface OnboardingStep {
  id: number;
  title: string;
  subtitle: string;
  description: string;
  icon: string;
  color: string;
  features?: string[];
  hotspots?: HotspotData[];
}

export interface HotspotData {
  id: string;
  x: number;
  y: number;
  title: string;
  description: string;
}

export const onboardingSteps: OnboardingStep[] = [
  {
    id: 1,
    title: "Welcome to ContentForge AI",
    subtitle: "Your Content Creation Journey Begins",
    description: "Transform your ideas into engaging content across 20+ platforms with the power of artificial intelligence.",
    icon: "Sparkles",
    color: "from-blue-500 to-violet-500",
    features: [
      "AI-powered content repurposing",
      "Multi-platform distribution",
      "Team collaboration tools",
      "Advanced analytics insights"
    ]
  },
  {
    id: 2,
    title: "Your Command Center",
    subtitle: "Dashboard Overview",
    description: "Everything you need at a glance - projects, analytics, and quick actions all in one place.",
    icon: "LayoutDashboard",
    color: "from-violet-500 to-purple-500",
    features: [
      "Projects overview with quick access",
      "Real-time analytics preview",
      "Quick action shortcuts",
      "Recent activity feed"
    ],
    hotspots: [
      { id: "projects", x: 20, y: 30, title: "Projects", description: "View and manage all your content projects" },
      { id: "analytics", x: 70, y: 25, title: "Analytics", description: "Track performance metrics at a glance" },
      { id: "actions", x: 50, y: 60, title: "Quick Actions", description: "Create content, invite team, view settings" }
    ]
  },
  {
    id: 3,
    title: "Create Content Your Way",
    subtitle: "Multiple Input Methods",
    description: "Import from URLs, paste text directly, or upload files - our AI handles the rest with intelligent processing.",
    icon: "FileInput",
    color: "from-purple-500 to-pink-500",
    features: [
      "URL import with smart scraping",
      "Direct text input with formatting",
      "File upload with drag-and-drop",
      "Support for videos, PDFs, and more"
    ],
    hotspots: [
      { id: "url", x: 25, y: 40, title: "URL Import", description: "Paste any URL to extract and repurpose content" },
      { id: "text", x: 50, y: 40, title: "Text Input", description: "Type or paste text directly into the editor" },
      { id: "upload", x: 75, y: 40, title: "File Upload", description: "Drag and drop files for AI processing" }
    ]
  },
  {
    id: 4,
    title: "AI-Powered Magic",
    subtitle: "Intelligent Content Generation",
    description: "Watch as AI transforms your content into multiple formats instantly - from blog posts to social media.",
    icon: "Wand2",
    color: "from-pink-500 to-rose-500",
    features: [
      "Automatic format conversion",
      "Tone and style adaptation",
      "Platform-specific optimization",
      "One-click generation"
    ],
    hotspots: [
      { id: "formats", x: 50, y: 35, title: "Output Formats", description: "Choose from 20+ content formats" },
      { id: "preview", x: 50, y: 65, title: "Live Preview", description: "See generated content before publishing" }
    ]
  },
  {
    id: 5,
    title: "Organize Your Assets",
    subtitle: "Asset Management",
    description: "Keep your content organized with folders, tags, and powerful search capabilities.",
    icon: "FolderOpen",
    color: "from-rose-500 to-orange-500",
    features: [
      "Folder creation and nesting",
      "Tag-based organization",
      "Bulk operations and actions",
      "Trash with recovery"
    ],
    hotspots: [
      { id: "folders", x: 30, y: 35, title: "Folders", description: "Create nested folder structures" },
      { id: "tags", x: 70, y: 35, title: "Tags", description: "Tag content for easy filtering" },
      { id: "search", x: 50, y: 70, title: "Search", description: "Find content instantly with AI search" }
    ]
  },
  {
    id: 6,
    title: "Work Together",
    subtitle: "Team Collaboration",
    description: "Invite team members, assign roles, and collaborate seamlessly on content projects.",
    icon: "Users",
    color: "from-orange-500 to-amber-500",
    features: [
      "Role-based access control",
      "Real-time collaboration",
      "Comment and feedback system",
      "Activity tracking"
    ],
    hotspots: [
      { id: "invite", x: 35, y: 40, title: "Invite Members", description: "Send invites via email or link" },
      { id: "roles", x: 65, y: 40, title: "Manage Roles", description: "Set permissions for each team member" }
    ]
  },
  {
    id: 7,
    title: "Insights That Matter",
    subtitle: "Analytics Overview",
    description: "Track performance, understand engagement, and optimize your content strategy with data.",
    icon: "BarChart3",
    color: "from-amber-500 to-yellow-500",
    features: [
      "Engagement rate tracking",
      "Platform performance comparison",
      "Content performance metrics",
      "Exportable reports"
    ],
    hotspots: [
      { id: "engagement", x: 25, y: 35, title: "Engagement", description: "Track likes, shares, and comments" },
      { id: "platforms", x: 75, y: 35, title: "Platforms", description: "Compare performance across channels" },
      { id: "trends", x: 50, y: 70, title: "Trends", description: "View performance trends over time" }
    ]
  },
  {
    id: 8,
    title: "Flexible Plans",
    subtitle: "Subscription & Billing",
    description: "From free to enterprise - choose the plan that works best for your content needs.",
    icon: "CreditCard",
    color: "from-yellow-500 to-lime-500",
    features: [
      "Free tier with 3 projects",
      "Pro with unlimited projects",
      "Enterprise with custom features",
      "Easy upgrade/downgrade"
    ],
    hotspots: [
      { id: "free", x: 20, y: 45, title: "Free Plan", description: "3 projects, basic features" },
      { id: "pro", x: 50, y: 40, title: "Pro Plan", description: "Unlimited projects, AI features" },
      { id: "enterprise", x: 80, y: 45, title: "Enterprise", description: "Custom solutions and support" }
    ]
  },
  {
    id: 9,
    title: "Make It Yours",
    subtitle: "Settings & Preferences",
    description: "Customize your experience with themes, notifications, and integrations.",
    icon: "Settings",
    color: "from-lime-500 to-green-500",
    features: [
      "Dark and light mode",
      "Notification preferences",
      "API keys and webhooks",
      "Profile customization"
    ],
    hotspots: [
      { id: "theme", x: 30, y: 40, title: "Theme", description: "Switch between light and dark modes" },
      { id: "notifications", x: 70, y: 40, title: "Notifications", description: "Configure alert preferences" }
    ]
  },
  {
    id: 10,
    title: "You're All Set!",
    subtitle: "Ready to Create",
    description: "Start creating amazing content with ContentForge AI. Your journey to content excellence begins now.",
    icon: "Rocket",
    color: "from-green-500 to-emerald-500",
    features: [
      "Create your first project",
      "Explore AI templates",
      "Invite your team",
      "Check out the documentation"
    ]
  }
];

export const quickTips = [
  {
    title: "Keyboard Shortcuts",
    description: "Press Cmd/Ctrl + K to open the command palette anytime",
    icon: "Keyboard"
  },
  {
    title: "Quick Create",
    description: "Use the + button in the sidebar for instant content creation",
    icon: "Zap"
  },
  {
    title: "Templates",
    description: "Browse 50+ templates in the Template Gallery for inspiration",
    icon: "LayoutTemplate"
  },
  {
    title: "Help Center",
    description: "Access guides and tutorials from the Help icon in settings",
    icon: "HelpCircle"
  }
];

export const getStepById = (id: number): OnboardingStep | undefined => {
  return onboardingSteps.find(step => step.id === id);
};

export const getTotalSteps = (): number => onboardingSteps.length;

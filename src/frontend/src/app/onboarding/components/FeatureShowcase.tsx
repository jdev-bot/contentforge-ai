'use client';

import { motion } from 'framer-motion';
import { 
  LayoutDashboard, FileInput, Wand2, FolderOpen, Users, BarChart3, 
  CreditCard, Settings, Check, Sparkles, FileText, Link, Upload, 
  Video, Image, Type, Share2, MessageSquare, TrendingUp, Eye,
  Zap, Crown, Building2, Bell, Palette, Key, UserCircle, Rocket
} from 'lucide-react';
import { OnboardingStep } from '../data/steps';
import { HotspotDemo } from './Hotspot';
import { staggerContainer, staggerItem, cardEntrance } from '../animations/variants';

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  LayoutDashboard,
  FileInput,
  Wand2,
  FolderOpen,
  Users,
  BarChart3,
  CreditCard,
  Settings,
  Sparkles,
  Rocket
};

interface FeatureShowcaseProps {
  step: OnboardingStep;
  hotspotsRevealed: Record<string, boolean>;
  onToggleHotspot: (id: string) => void;
}

export function FeatureShowcase({ step, hotspotsRevealed, onToggleHotspot }: FeatureShowcaseProps) {
  const Icon = iconMap[step.icon] || Sparkles;

  // Get specific content based on step
  const renderStepContent = () => {
    switch (step.id) {
      case 2:
        return <DashboardContent />;
      case 3:
        return <ContentCreationContent />;
      case 4:
        return <AIGenerationContent />;
      case 5:
        return <AssetManagementContent />;
      case 6:
        return <TeamCollaborationContent />;
      case 7:
        return <AnalyticsContent />;
      case 8:
        return <SubscriptionContent />;
      case 9:
        return <SettingsContent />;
      default:
        return null;
    }
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20 min-h-screen flex flex-col justify-center"
    >
      {/* Header */}
      <motion.div variants={staggerItem} className="text-center mb-10">
        {/* Step Icon */}
        <motion.div
          className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${step.color} mb-6 shadow-lg`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Icon className="w-8 h-8 text-white" />
        </motion.div>

        {/* Step Number Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-sm font-medium mb-4">
          <span className="flex items-center justify-center w-5 h-5 rounded-full bg-gradient-to-r from-blue-500 to-violet-500 text-white text-xs">
            {step.id}
          </span>
          Step {step.id} of 10
        </div>

        {/* Title */}
        <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 dark:text-white mb-3">
          {step.title}
        </h2>

        {/* Subtitle */}
        <p className="text-lg sm:text-xl text-slate-500 dark:text-slate-400">
          {step.subtitle}
        </p>
      </motion.div>

      {/* Description */}
      <motion.div variants={staggerItem} className="text-center mb-10 max-w-2xl mx-auto">
        <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
          {step.description}
        </p>
      </motion.div>

      {/* Interactive Demo or Visual Content */}
      <motion.div variants={staggerItem} className="mb-10">
        {step.hotspots ? (
          <HotspotDemo
            hotspots={step.hotspots}
            revealedHotspots={hotspotsRevealed}
            onToggleHotspot={onToggleHotspot}
          />
        ) : (
          renderStepContent()
        )}
      </motion.div>

      {/* Feature List */}
      <motion.div variants={staggerItem}>
        <div className="glass-card rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
            <Check className="w-5 h-5 text-emerald-500" />
            Key Features
          </h3>
          <div className="grid sm:grid-cols-2 gap-4">
            {step.features?.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex items-start gap-3"
              >
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mt-0.5">
                  <Check className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                </div>
                <span className="text-slate-600 dark:text-slate-300 text-sm">{feature}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

// Dashboard Content
function DashboardContent() {
  return (
    <div className="grid sm:grid-cols-3 gap-4">
      {[
        { title: 'Projects', count: '12 Active', color: 'from-blue-500 to-violet-500', icon: FolderOpen },
        { title: 'Analytics', count: '+24% Growth', color: 'from-violet-500 to-purple-500', icon: TrendingUp },
        { title: 'Team', count: '5 Members', color: 'from-purple-500 to-pink-500', icon: Users }
      ].map((card, i) => (
        <motion.div
          key={card.title}
          variants={cardEntrance}
          custom={i}
          whileHover={{ y: -4, scale: 1.02 }}
          className="glass-card rounded-xl p-5"
        >
          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${card.color} flex items-center justify-center mb-3`}>
            <card.icon className="w-5 h-5 text-white" />
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">{card.title}</p>
          <p className="text-xl font-semibold text-slate-900 dark:text-white">{card.count}</p>
        </motion.div>
      ))}
    </div>
  );
}

// Content Creation Content
function ContentCreationContent() {
  const methods = [
    { icon: Link, label: 'URL Import', color: 'from-blue-500 to-cyan-500' },
    { icon: Type, label: 'Text Input', color: 'from-violet-500 to-purple-500' },
    { icon: Upload, label: 'File Upload', color: 'from-pink-500 to-rose-500' }
  ];

  return (
    <div className="grid sm:grid-cols-3 gap-4">
      {methods.map((method, i) => (
        <motion.div
          key={method.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          whileHover={{ scale: 1.05 }}
          className="glass-card rounded-xl p-6 text-center cursor-pointer group"
        >
          <div className={`w-14 h-14 mx-auto rounded-xl bg-gradient-to-br ${method.color} flex items-center justify-center mb-4 shadow-lg group-hover:shadow-xl transition-shadow`}>
            <method.icon className="w-7 h-7 text-white" />
          </div>
          <p className="font-medium text-slate-900 dark:text-white">{method.label}</p>
        </motion.div>
      ))}
    </div>
  );
}

// AI Generation Content
function AIGenerationContent() {
  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex flex-col sm:flex-row items-center gap-6">
        {/* Input Side */}
        <div className="flex-1 w-full">
          <div className="bg-slate-100 dark:bg-slate-800 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <FileText className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-medium text-slate-500">Input</span>
            </div>
            <div className="space-y-2">
              <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full w-3/4" />
              <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full w-full" />
              <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full w-5/6" />
            </div>
          </div>
        </div>

        {/* Arrow */}
        <motion.div
          animate={{ x: [0, 5, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="flex-shrink-0"
        >
          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-violet-500 to-pink-500 flex items-center justify-center shadow-lg">
            <Wand2 className="w-6 h-6 text-white" />
          </div>
        </motion.div>

        {/* Output Side */}
        <div className="flex-1 w-full">
          <div className="grid grid-cols-2 gap-2">
            {[
              { icon: Video, label: 'Video' },
              { icon: Image, label: 'Image' },
              { icon: Share2, label: 'Social' },
              { icon: FileText, label: 'Blog' }
            ].map((item, i) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5 + i * 0.1 }}
                className="bg-gradient-to-br from-blue-50 to-violet-50 dark:from-blue-900/20 dark:to-violet-900/20 rounded-lg p-3 text-center border border-blue-100 dark:border-blue-800"
              >
                <item.icon className="w-5 h-5 mx-auto mb-1 text-blue-500" />
                <span className="text-xs text-slate-600 dark:text-slate-400">{item.label}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Asset Management Content
function AssetManagementContent() {
  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FolderOpen className="w-5 h-5 text-blue-500" />
          <span className="font-medium text-slate-900 dark:text-white">My Assets</span>
        </div>
        <div className="flex gap-2">
          <div className="px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-xs text-slate-600 dark:text-slate-400">All</div>
          <div className="px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-xs text-blue-600 dark:text-blue-400">Images</div>
          <div className="px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-xs text-slate-600 dark:text-slate-400">Videos</div>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            className="aspect-square rounded-lg bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-700 flex items-center justify-center"
          >
            <div className="w-6 h-6 rounded bg-slate-300 dark:bg-slate-600" />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

// Team Collaboration Content
function TeamCollaborationContent() {
  const members = [
    { name: 'You', role: 'Admin', color: 'from-blue-500 to-violet-500' },
    { name: 'Alice', role: 'Editor', color: 'from-violet-500 to-purple-500' },
    { name: 'Bob', role: 'Editor', color: 'from-purple-500 to-pink-500' },
    { name: 'Carol', role: 'Viewer', color: 'from-pink-500 to-rose-500' }
  ];

  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-blue-500" />
          <span className="font-medium text-slate-900 dark:text-white">Team Members</span>
        </div>
        <button className="px-3 py-1.5 rounded-lg bg-blue-500 text-white text-sm font-medium">
          Invite
        </button>
      </div>
      <div className="space-y-3">
        {members.map((member, i) => (
          <motion.div
            key={member.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50"
          >
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${member.color} flex items-center justify-center text-white font-medium`}>
                {member.name[0]}
              </div>
              <div>
                <p className="font-medium text-slate-900 dark:text-white text-sm">{member.name}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">{member.role}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-slate-400" />
              <Eye className="w-4 h-4 text-slate-400" />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

// Analytics Content
function AnalyticsContent() {
  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-blue-500" />
          <span className="font-medium text-slate-900 dark:text-white">Performance Overview</span>
        </div>
        <select className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-sm text-slate-600 dark:text-slate-400 border-none">
          <option>Last 7 days</option>
          <option>Last 30 days</option>
        </select>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Views', value: '24.5K', change: '+12%' },
          { label: 'Engagement', value: '8.2%', change: '+5%' },
          { label: 'Shares', value: '1.2K', change: '+18%' }
        ].map((stat, i) => (
          <div key={stat.label} className="text-center">
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{stat.value}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">{stat.label}</p>
            <span className="text-xs text-emerald-500 font-medium">{stat.change}</span>
          </div>
        ))}
      </div>

      {/* Mock Chart */}
      <div className="h-32 flex items-end justify-between gap-2">
        {[40, 65, 45, 80, 55, 90, 70].map((height, i) => (
          <motion.div
            key={i}
            initial={{ height: 0 }}
            animate={{ height: `${height}%` }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            className="flex-1 rounded-t-lg bg-gradient-to-t from-blue-500/20 to-blue-500"
          />
        ))}
      </div>
    </div>
  );
}

// Subscription Content
function SubscriptionContent() {
  const plans = [
    { name: 'Free', price: '$0', features: ['3 Projects', 'Basic AI', 'Email Support'], current: false },
    { name: 'Pro', price: '$29', features: ['Unlimited', 'Advanced AI', 'Priority Support'], current: true },
    { name: 'Enterprise', price: 'Custom', features: ['Custom', 'Dedicated', '24/7 Support'], current: false }
  ];

  return (
    <div className="grid sm:grid-cols-3 gap-4">
      {plans.map((plan, i) => (
        <motion.div
          key={plan.name}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className={`rounded-2xl p-5 ${
            plan.current 
              ? 'bg-gradient-to-br from-blue-500 to-violet-500 text-white' 
              : 'glass-card'
          }`}
        >
          <div className="flex items-center gap-2 mb-3">
            {plan.name === 'Free' && <Zap className="w-4 h-4" />}
            {plan.name === 'Pro' && <Crown className="w-4 h-4" />}
            {plan.name === 'Enterprise' && <Building2 className="w-4 h-4" />}
            <span className="font-semibold">{plan.name}</span>
            {plan.current && <span className="ml-auto text-xs bg-white/20 px-2 py-0.5 rounded-full">Current</span>}
          </div>
          
          <p className={`text-2xl font-bold mb-4 ${plan.current ? 'text-white' : 'text-slate-900 dark:text-white'}`}>
            {plan.price}<span className="text-sm font-normal text-slate-500">{plan.price !== 'Custom' && '/mo'}</span>
          </p>
          
          <ul className="space-y-2">
            {plan.features.map((feature) => (
              <li key={feature} className={`flex items-center gap-2 text-sm ${plan.current ? 'text-white/90' : 'text-slate-600 dark:text-slate-300'}`}>
                <Check className="w-4 h-4 flex-shrink-0" />
                {feature}
              </li>
            ))}
          </ul>
        </motion.div>
      ))}
    </div>
  );
}

// Settings Content
function SettingsContent() {
  return (
    <div className="glass-card rounded-2xl p-6">
      <div className="space-y-4">
        {/* Theme Setting */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
              <Palette className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-medium text-slate-900 dark:text-white">Appearance</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Dark mode, accent colors</p>
            </div>
          </div>
          <div className="w-12 h-6 rounded-full bg-blue-500 relative">
            <div className="absolute right-1 top-1 w-4 h-4 rounded-full bg-white" />
          </div>
        </motion.div>

        {/* Notifications */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-rose-400 to-pink-500 flex items-center justify-center">
              <Bell className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-medium text-slate-900 dark:text-white">Notifications</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Email, push, Slack</p>
            </div>
          </div>
          <div className="w-12 h-6 rounded-full bg-slate-300 dark:bg-slate-600 relative">
            <div className="absolute left-1 top-1 w-4 h-4 rounded-full bg-white" />
          </div>
        </motion.div>

        {/* API Keys */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
              <Key className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-medium text-slate-900 dark:text-white">API Keys</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Manage integrations</p>
            </div>
          </div>
          <button className="px-3 py-1.5 rounded-lg bg-slate-200 dark:bg-slate-700 text-sm font-medium text-slate-700 dark:text-slate-300">
            Manage
          </button>
        </motion.div>
      </div>
    </div>
  );
}

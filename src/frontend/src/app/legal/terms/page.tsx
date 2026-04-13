import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Terms of Service - ContentForge AI',
  description: 'Read the Terms of Service for using ContentForge AI platform.',
}

export default function TermsOfService() {
  const lastUpdated = 'April 13, 2026'

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link 
            href="/" 
            className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium"
          >
            ← Back to Home
          </Link>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-4">
            Terms of Service
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mb-8">
            Last Updated: {lastUpdated}
          </p>

          <div className="prose dark:prose-invert max-w-none">
            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                1. Acceptance of Terms
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                By accessing or using ContentForge AI (&quot;the Service&quot;), you agree to be bound by these 
                Terms of Service (&quot;Terms&quot;). If you disagree with any part of the terms, you may not 
                access the Service.
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                These Terms apply to all visitors, users, and others who access or use the Service.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                2. Description of Service
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                ContentForge AI is an AI-powered content repurposing and distribution platform that allows 
                users to transform content into multiple formats and distribute it across various platforms.
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                We reserve the right to modify or discontinue the Service at any time, with or without notice.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                3. User Accounts
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                To use certain features of the Service, you must register for an account. You agree to:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Provide accurate, current, and complete information during registration</li>
                <li>Maintain and promptly update your account information</li>
                <li>Maintain the security of your password and accept all risks of unauthorized access</li>
                <li>Notify us immediately of any unauthorized use of your account</li>
                <li>Not share your account credentials with any third party</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                4. Subscription and Payments
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                Some aspects of the Service may be available only with a paid subscription. By subscribing:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>You agree to pay all fees associated with your subscription plan</li>
                <li>Subscription fees are billed in advance on a monthly or annual basis</li>
                <li>You may cancel your subscription at any time, with access continuing until the end of the billing period</li>
                <li>We do not provide refunds for partial months or unused credits</li>
                <li>We reserve the right to change subscription fees upon notice</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                5. User Content
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                You retain all rights to the content you upload, submit, or generate using the Service 
                (&quot;User Content&quot;).
              </p>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                By uploading User Content, you grant ContentForge AI a limited license to:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Process your content to provide the Service</li>
                <li>Store your content on our servers</li>
                <li>Transmit your content to third-party platforms at your direction</li>
              </ul>
              <p className="text-slate-600 dark:text-slate-400">
                You represent that you have the necessary rights to grant us this license for any User Content.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                6. Acceptable Use
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                You agree not to use the Service to:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Generate or distribute content that is illegal, harmful, threatening, abusive, harassing, defamatory, vulgar, obscene, or otherwise objectionable</li>
                <li>Impersonate any person or entity</li>
                <li>Upload viruses, malware, or other malicious code</li>
                <li>Interfere with or disrupt the Service or servers</li>
                <li>Attempt to gain unauthorized access to any portion of the Service</li>
                <li>Use the Service for any illegal purpose</li>
                <li>Violate any applicable laws or regulations</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                7. Intellectual Property
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                The Service and its original content (excluding User Content), features, and functionality 
                are and will remain the exclusive property of ContentForge AI and its licensors. The 
                Service is protected by copyright, trademark, and other laws.
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                Our trademarks and trade dress may not be used in connection with any product or service 
                without our prior written consent.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                8. Termination
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                We may terminate or suspend your account immediately, without prior notice or liability, 
                for any reason whatsoever, including without limitation if you breach the Terms.
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                Upon termination, your right to use the Service will immediately cease. If you wish to 
                terminate your account, you may simply discontinue using the Service or contact us to 
                request account deletion.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                9. Limitation of Liability
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                In no event shall ContentForge AI, nor its directors, employees, partners, agents, 
                suppliers, or affiliates, be liable for any indirect, incidental, special, consequential, 
                or punitive damages, including without limitation, loss of profits, data, use, goodwill, 
                or other intangible losses.
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                Our total liability to you for all claims arising from or relating to these Terms or 
                your use of the Service shall not exceed the amount you paid us (if any) in the twelve 
                (12) months preceding the claim.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                10. Disclaimer
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                Your use of the Service is at your sole risk. The Service is provided on an &quot;AS IS&quot; and 
                &quot;AS AVAILABLE&quot; basis. We make no warranties, expressed or implied, regarding the Service, 
                including but not limited to implied warranties of merchantability, fitness for a particular 
                purpose, non-infringement, or course of performance.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                11. Governing Law
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                These Terms shall be governed and construed in accordance with the laws of the United 
                States, without regard to its conflict of law provisions. Our failure to enforce any 
                right or provision of these Terms will not be considered a waiver of those rights.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                12. Changes to Terms
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                We reserve the right, at our sole discretion, to modify or replace these Terms at any 
                time. If a revision is material, we will provide at least 30 days&apos; notice prior to any 
                new terms taking effect. What constitutes a material change will be determined at our sole 
                discretion.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                13. Contact Us
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                If you have any questions about these Terms, please contact us at{' '}
                <a href="mailto:legal@contentforge.ai" className="text-blue-600 hover:underline">
                  legal@contentforge.ai
                </a>.
              </p>
            </section>
          </div>
        </div>

        {/* Footer Links */}
        <div className="mt-8 flex flex-wrap justify-center gap-6 text-sm text-slate-500 dark:text-slate-400">
          <Link href="/legal/terms" className="hover:text-slate-700 dark:hover:text-slate-300">Terms of Service</Link>
          <Link href="/legal/privacy" className="hover:text-slate-700 dark:hover:text-slate-300">Privacy Policy</Link>
          <Link href="/legal/cookies" className="hover:text-slate-700 dark:hover:text-slate-300">Cookie Policy</Link>
          <Link href="/legal/dmca" className="hover:text-slate-700 dark:hover:text-slate-300">DMCA Notice</Link>
        </div>
      </div>
    </div>
  )
}

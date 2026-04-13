import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Privacy Policy - ContentForge AI',
  description: 'Read our Privacy Policy to understand how we collect, use, and protect your data.',
}

export default function PrivacyPolicy() {
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
            Privacy Policy
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mb-8">
            Last Updated: {lastUpdated}
          </p>

          <div className="prose dark:prose-invert max-w-none">
            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                1. Introduction
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                ContentForge AI (&quot;we,&quot; &quot;our,&quot; or &quot;us&quot;) is committed to protecting your privacy. 
                This Privacy Policy explains how we collect, use, disclose, and safeguard your information 
                when you use our website, application, and services (collectively, the &quot;Service&quot;).
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                By accessing or using the Service, you agree to the collection and use of information in 
                accordance with this Privacy Policy. If you do not agree with the terms of this Privacy 
                Policy, please do not access the Service.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                2. Information We Collect
              </h2>
              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-3">
                2.1 Personal Information
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                We may collect personal information that you voluntarily provide to us when you:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Register for an account</li>
                <li>Subscribe to our services</li>
                <li>Contact our support team</li>
                <li>Upload content for processing</li>
                <li>Participate in surveys or promotions</li>
              </ul>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                This information may include:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Name and email address</li>
                <li>Billing information (processed securely by our payment processor)</li>
                <li>Account credentials</li>
                <li>Content you upload or generate</li>
                <li>Communication preferences</li>
              </ul>

              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-3">
                2.2 Automatically Collected Information
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                When you access the Service, we may automatically collect certain information, including:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>IP address and device information</li>
                <li>Browser type and version</li>
                <li>Operating system</li>
                <li>Usage patterns and preferences</li>
                <li>Cookies and similar tracking technologies (see Cookie Policy)</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                3. How We Use Your Information
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                We use the information we collect for various purposes, including:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Providing and maintaining the Service</li>
                <li>Processing transactions and sending related information</li>
                <li>Personalizing your experience and content recommendations</li>
                <li>Improving our services and developing new features</li>
                <li>Communicating with you about updates, security alerts, and support</li>
                <li>Sending promotional emails (with your consent, which you can withdraw)</li>
                <li>Preventing fraud and ensuring security</li>
                <li>Complying with legal obligations</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                4. Legal Basis for Processing (GDPR)
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                If you are in the European Union, our legal basis for collecting and using your personal 
                information depends on the information collected and the specific context. We process your 
                personal information based on:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li><strong>Contract Performance:</strong> Processing necessary to fulfill our contractual obligations to you</li>
                <li><strong>Consent:</strong> Where you have given specific consent</li>
                <li><strong>Legitimate Interests:</strong> Where processing is necessary for our legitimate interests</li>
                <li><strong>Legal Obligation:</strong> Where required by law</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                5. Data Retention
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                We retain your personal information only for as long as necessary to fulfill the purposes 
                for which it was collected, including satisfying legal, accounting, or reporting requirements. 
                Content you upload is retained until you delete it or your account is closed. Account information 
                is retained for 30 days after account deletion (see Account Deletion section).
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                6. Your Data Protection Rights
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                Depending on your location, you may have the following rights:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li><strong>Access:</strong> Request copies of your personal information</li>
                <li><strong>Rectification:</strong> Request correction of inaccurate information</li>
                <li><strong>Erasure:</strong> Request deletion of your personal information</li>
                <li><strong>Restriction:</strong> Request restriction of processing</li>
                <li><strong>Data Portability:</strong> Request transfer of your data</li>
                <li><strong>Objection:</strong> Object to processing of your personal information</li>
              </ul>
              <p className="text-slate-600 dark:text-slate-400">
                To exercise these rights, please contact us using the information provided in the 
                &quot;Contact Us&quot; section below.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                7. Information Sharing and Disclosure
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                We do not sell, trade, or rent your personal information to third parties. We may share 
                your information in the following circumstances:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li><strong>Service Providers:</strong> With third-party vendors who assist in operating our Service</li>
                <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale</li>
                <li><strong>Legal Requirements:</strong> When required by law or legal process</li>
                <li><strong>Protection:</strong> To protect our rights, property, or safety</li>
                <li><strong>With Your Consent:</strong> When you have given us permission</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                8. Data Security
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                We implement appropriate technical and organizational measures to protect your personal 
                information. However, no method of transmission over the Internet or electronic storage 
                is 100% secure. While we strive to use commercially acceptable means to protect your 
                information, we cannot guarantee absolute security.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                9. International Data Transfers
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                Your information may be transferred to and maintained on computers located outside of your 
                state, province, country, or other governmental jurisdiction where data protection laws may 
                differ. We ensure appropriate safeguards are in place for such transfers in accordance 
                with applicable data protection laws.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                10. Children&apos;s Privacy
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                Our Service is not intended for use by children under the age of 16. We do not knowingly 
                collect personally identifiable information from children under 16. If you are a parent 
                or guardian and believe your child has provided us with personal information, please contact 
                us immediately.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                11. Account Deletion
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                You may request deletion of your account at any time through your account settings. Upon 
                deletion:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Your account will be marked for deletion with a 30-day grace period</li>
                <li>During the grace period, you can restore your account by logging in</li>
                <li>After 30 days, your personal information will be permanently deleted</li>
                <li>Some anonymized usage data may be retained for analytics purposes</li>
                <li>Legal obligations may require retention of certain information</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                12. Changes to This Privacy Policy
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                We may update our Privacy Policy from time to time. We will notify you of any changes by 
                posting the new Privacy Policy on this page and updating the &quot;Last Updated&quot; date. You 
                are advised to review this Privacy Policy periodically for any changes.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                13. Contact Us
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                If you have any questions about this Privacy Policy or our data practices, please contact us:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2">
                <li>By email:{' '}
                  <a href="mailto:privacy@contentforge.ai" className="text-blue-600 hover:underline">
                    privacy@contentforge.ai
                  </a>
                </li>
                <li>Through your account settings for data-related requests</li>
              </ul>
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

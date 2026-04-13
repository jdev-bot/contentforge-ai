import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Cookie Policy - ContentForge AI',
  description: 'Learn about how we use cookies and similar technologies.',
}

export default function CookiePolicy() {
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
            Cookie Policy
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mb-8">
            Last Updated: {lastUpdated}
          </p>

          <div className="prose dark:prose-invert max-w-none">
            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                What Are Cookies
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                Cookies are small text files that are stored on your computer or mobile device when you 
                visit a website. They are widely used to make websites work more efficiently and provide 
                useful information to website owners.
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                In addition to cookies, we may use other similar technologies such as local storage, 
                session storage, and pixel tags to collect information about your browsing activities.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                How We Use Cookies
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                ContentForge AI uses cookies for the following purposes:
              </p>
              
              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
                Essential Cookies (Required)
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                These cookies are necessary for the website to function properly. They enable core 
                functionality such as security, network management, and account access. You cannot opt 
                out of these cookies.
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Authentication and session management</li>
                <li>Security features and fraud prevention</li>
                <li>Load balancing and server routing</li>
                <li>Cookie consent preferences storage</li>
              </ul>

              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
                Functional Cookies
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                These cookies enable enhanced functionality and personalization, such as remembering 
                your preferences and settings.
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Theme preferences (light/dark mode)</li>
                <li>Language preferences</li>
                <li>UI customization settings</li>
                <li>Recently viewed items</li>
              </ul>

              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
                Analytics Cookies
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                These cookies help us understand how visitors interact with our website by collecting 
                and reporting information anonymously.
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Page view statistics</li>
                <li>Feature usage tracking</li>
                <li>Error monitoring and debugging</li>
                <li>Performance metrics</li>
              </ul>

              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
                Marketing Cookies (Optional)
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                These cookies may be set through our site by our advertising partners to build a profile 
                of your interests and show you relevant advertisements on other sites.
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li>Ad delivery and retargeting</li>
                <li>Campaign effectiveness tracking</li>
                <li>Social media integration</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Third-Party Cookies
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                We may allow third-party service providers to place cookies on your device for the 
                following purposes:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li><strong>Supabase:</strong> Authentication and database services</li>
                <li><strong>Stripe:</strong> Payment processing (when applicable)</li>
                <li><strong>Analytics Providers:</strong> Usage statistics and insights</li>
              </ul>
              <p className="text-slate-600 dark:text-slate-400">
                These third parties have their own privacy and cookie policies. We recommend that 
                you review their policies for more information.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Cookie Duration
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                Cookies can be categorized by their lifespan:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li><strong>Session Cookies:</strong> Temporary cookies that expire when you close your browser</li>
                <li><strong>Persistent Cookies:</strong> Cookies that remain on your device for a set period or until deleted</li>
              </ul>
              <p className="text-slate-600 dark:text-slate-400">
                Most persistent cookies have an expiration date ranging from a few days to several months. 
                Cookie consent preferences are typically stored for 12 months before requiring renewal.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Managing Your Cookie Preferences
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                You have the right to accept or reject cookies. You can manage your preferences in several ways:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li><strong>Cookie Consent Banner:</strong> Adjust your preferences using the cookie banner when you first visit our site</li>
                <li><strong>Browser Settings:</strong> Most web browsers allow you to control cookies through their settings</li>
                <li><strong>Third-Party Tools:</strong> Use browser extensions or privacy tools to manage cookies</li>
              </ul>
              <p className="text-slate-600 dark:text-slate-400">
                Please note that blocking some types of cookies may impact your experience on our website 
                and the services we are able to offer.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                How to Delete Cookies
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                You can delete cookies that are already stored on your device:
              </p>
              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400 space-y-2 mb-4">
                <li><strong>Chrome:</strong> Settings → Privacy and security → Clear browsing data → Cookies</li>
                <li><strong>Firefox:</strong> Settings → Privacy &amp; Security → Cookies and Site Data → Clear Data</li>
                <li><strong>Safari:</strong> Preferences → Privacy → Manage Website Data → Remove All</li>
                <li><strong>Edge:</strong> Settings → Privacy, search, and services → Clear browsing data</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Do Not Track
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                Some browsers have a &quot;Do Not Track&quot; feature that signals websites that you do not want 
                to have your online activities tracked. Currently, we do not respond to &quot;Do Not Track&quot; 
                signals. However, you can use our cookie consent banner to manage your tracking preferences.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Updates to This Policy
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                We may update this Cookie Policy from time to time to reflect changes in technology, 
                regulation, or our business operations. Any changes will be posted on this page with 
                an updated revision date.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Contact Us
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                If you have any questions about our use of cookies or this Cookie Policy, please contact us at{' '}
                <a href="mailto:privacy@contentforge.ai" className="text-blue-600 hover:underline">
                  privacy@contentforge.ai
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

import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'DMCA Notice - ContentForge AI',
  description: 'Information about copyright infringement claims and DMCA takedown procedures.',
}

export default function DMCANotice() {
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
            DMCA Notice &amp; Takedown Policy
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mb-8">
            Last Updated: {lastUpdated}
          </p>

          <div className="prose dark:prose-invert max-w-none">
            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Introduction
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                ContentForge AI respects the intellectual property rights of others and expects users 
                of our Service to do the same. In accordance with the Digital Millennium Copyright Act 
                of 1998 (&quot;DMCA&quot;), we have adopted the following policy regarding copyright infringement.
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                If you believe that material available on or through our Service infringes upon your 
                copyright, please notify us using the procedure outlined below.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Reporting Copyright Infringement
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                If you are a copyright owner or an agent thereof and believe that any content on 
                ContentForge AI infringes upon your copyrights, you may submit a notification pursuant 
                to the DMCA by providing our Designated Agent with the following information in writing:
              </p>
              
              <ol className="list-decimal list-inside text-slate-600 dark:text-slate-400 space-y-3 mb-4">
                <li>
                  A physical or electronic signature of a person authorized to act on behalf of the owner 
                  of an exclusive right that is allegedly infringed.
                </li>
                <li>
                  Identification of the copyrighted work claimed to have been infringed, or, if multiple 
                  copyrighted works at a single online site are covered by a single notification, a 
                  representative list of such works at that site.
                </li>
                <li>
                  Identification of the material that is claimed to be infringing or to be the subject 
                  of infringing activity and that is to be removed or access to which is to be disabled, 
                  and information reasonably sufficient to permit the service provider to locate the material. 
                  Please provide URLs to the specific content.
                </li>
                <li>
                  Information reasonably sufficient to permit the service provider to contact you, such 
                  as an address, telephone number, and, if available, an email address.
                </li>
                <li>
                  A statement that you have a good faith belief that use of the material in the manner 
                  complained of is not authorized by the copyright owner, its agent, or the law.
                </li>
                <li>
                  A statement that the information in the notification is accurate, and under penalty 
                  of perjury, that you are authorized to act on behalf of the owner of an exclusive 
                  right that is allegedly infringed.
                </li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Designated Agent Contact Information
              </h2>
              <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-6 border border-slate-200 dark:border-slate-700">
                <p className="text-slate-600 dark:text-slate-400 mb-2">
                  <strong>Copyright Agent</strong><br />
                  ContentForge AI<br />
                  Email:{' '}
                  <a href="mailto:dmca@contentforge.ai" className="text-blue-600 hover:underline">
                    dmca@contentforge.ai
                  </a>
                </p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-4">
                  Note: This email address is for copyright claims only. For other inquiries, please 
                  contact our general support.
                </p>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Counter-Notification
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                If you believe that your content that was removed (or to which access was disabled) is 
                not infringing, or that you have the authorization from the copyright owner, the 
                copyright owner&apos;s agent, or pursuant to the law, to post and use the material, you may 
                send a counter-notification containing the following information to the Designated Agent:
              </p>
              
              <ol className="list-decimal list-inside text-slate-600 dark:text-slate-400 space-y-3 mb-4">
                <li>Your physical or electronic signature.</li>
                <li>
                  Identification of the content that has been removed or to which access has been 
                  disabled and the location at which the content appeared before it was removed or 
                  disabled.
                </li>
                <li>
                  A statement under penalty of perjury that you have a good faith belief that the 
                  content was removed or disabled as a result of mistake or a misidentification.</li>
                <li>
                  Your name, address, and telephone number, and a statement that you consent to the 
                  jurisdiction of the federal court in the district where you are located (or if you are 
                  outside the United States, that you consent to jurisdiction of any judicial district 
                  in which the service provider may be found), and that you will accept service of 
                  process from the person who provided the original notification or an agent of such 
                  person.
                </li>
              </ol>
              
              <p className="text-slate-600 dark:text-slate-400">
                Upon receipt of a valid counter-notification, we will forward it to the party who 
                submitted the original claim of copyright infringement. Please note that under Section 
                512(f) of the DMCA, any person who knowingly materially misrepresents that material 
                or activity was removed or disabled by mistake or misidentification may be subject to 
                liability.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Repeat Infringers
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                It is our policy to terminate the accounts of users who are determined to be repeat 
                infringers. A repeat infringer is a user who has been notified of infringing activity 
                more than twice or has had infringing content removed from our Service more than twice.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Misrepresentation
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                Please note that under 17 U.S.C. § 512(f), any person who knowingly materially 
                misrepresents that material or activity is infringing, or that material or activity 
                was removed or disabled by mistake or misidentification, may be subject to liability 
                for damages, including costs and attorneys&apos; fees.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Trademarks
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                All trademarks, logos, and service marks displayed on the Service are the property of 
                their respective owners. Unauthorized use of any trademark displayed on the Service is 
                strictly prohibited.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Changes to This Policy
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                We reserve the right to modify this DMCA Policy at any time. Changes will be posted 
                on this page with an updated revision date. Your continued use of the Service after 
                any changes constitutes acceptance of the modified policy.
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

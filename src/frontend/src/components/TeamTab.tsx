'use client'

/**
 * Team management component.
 */
import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';

export default function TeamTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Team Management</h2>
      
      <Card>
        <CardContent className="p-6">
          <p className="text-gray-600 mb-4">
            Team features coming soon. This will allow you to:
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-2">
            <li>Create organizations</li>
            <li>Invite team members</li>
            <li>Manage roles and permissions</li>
            <li>Collaborate on content</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

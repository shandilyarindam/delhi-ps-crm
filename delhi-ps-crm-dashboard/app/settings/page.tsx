"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Settings as SettingsIcon, Shield, Bell, Globe } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="p-4 md:p-6 lg:p-8">
      <h1 className="mb-1 text-xl font-bold text-[#1B3A5C] md:text-2xl">Settings</h1>
      <p className="mb-4 text-xs text-slate-500 md:mb-6 md:text-sm">
        System configuration and preferences
      </p>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6">
        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <SettingsIcon className="h-4 w-4 text-[#1B3A5C]" />
              <CardTitle className="text-sm font-semibold text-[#1B3A5C]">
                General
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Auto-refresh interval
                </p>
                <p className="text-xs text-slate-400">
                  Dashboard data refresh frequency
                </p>
              </div>
              <Badge variant="outline" className="text-xs">
                30 seconds
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Default view
                </p>
                <p className="text-xs text-slate-400">
                  Landing page after login
                </p>
              </div>
              <Badge variant="outline" className="text-xs">
                Dashboard
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Timezone
                </p>
                <p className="text-xs text-slate-400">
                  Display timestamps in
                </p>
              </div>
              <Badge variant="outline" className="text-xs">
                IST (UTC+5:30)
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Bell className="h-4 w-4 text-[#1B3A5C]" />
              <CardTitle className="text-sm font-semibold text-[#1B3A5C]">
                Notifications
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  WhatsApp alerts
                </p>
                <p className="text-xs text-slate-400">
                  Officer assignment notifications
                </p>
              </div>
              <Badge variant="outline" className="bg-emerald-50 text-xs text-emerald-700">
                Enabled
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Email digests
                </p>
                <p className="text-xs text-slate-400">
                  Daily summary via SendGrid
                </p>
              </div>
              <Badge variant="outline" className="bg-emerald-50 text-xs text-emerald-700">
                Enabled
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Escalation alerts
                </p>
                <p className="text-xs text-slate-400">
                  Critical complaint notifications
                </p>
              </div>
              <Badge variant="outline" className="bg-emerald-50 text-xs text-emerald-700">
                Enabled
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-[#1B3A5C]" />
              <CardTitle className="text-sm font-semibold text-[#1B3A5C]">
                Security
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  API Access
                </p>
                <p className="text-xs text-slate-400">
                  Supabase RLS policies active
                </p>
              </div>
              <Badge variant="outline" className="bg-emerald-50 text-xs text-emerald-700">
                Protected
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Data residency
                </p>
                <p className="text-xs text-slate-400">
                  Complaint data storage region
                </p>
              </div>
              <Badge variant="outline" className="text-xs">
                India (Mumbai)
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 bg-white shadow-sm">
          <CardHeader className="border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-[#1B3A5C]" />
              <CardTitle className="text-sm font-semibold text-[#1B3A5C]">
                Integration
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Supabase
                </p>
                <p className="text-xs text-slate-400">
                  Database backend
                </p>
              </div>
              <Badge variant="outline" className="bg-emerald-50 text-xs text-emerald-700">
                Connected
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  Gemini 2.5 Flash-Lite
                </p>
                <p className="text-xs text-slate-400">
                  AI classification engine
                </p>
              </div>
              <Badge variant="outline" className="bg-emerald-50 text-xs text-emerald-700">
                Active
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">
                  WhatsApp Business API
                </p>
                <p className="text-xs text-slate-400">
                  Citizen messaging platform
                </p>
              </div>
              <Badge variant="outline" className="bg-emerald-50 text-xs text-emerald-700">
                Live
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

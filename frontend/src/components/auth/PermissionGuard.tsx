import React from "react";
import { useAuthStore } from "../../store/auth";

interface PermissionGuardProps {
  children: React.ReactNode;
  permissions?: string[];
  roles?: string[];
  fallback?: React.ReactNode;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  children,
  permissions = [],
  roles = [],
  fallback = null
}) => {
  const { user, accessToken } = useAuthStore();

  if (!user || !accessToken) return <>{fallback}</>;

  // Decode JWT access token payload to check roles and permissions
  try {
    const payloadBase64 = accessToken.split(".")[1];
    const payload = JSON.parse(window.atob(payloadBase64));
    
    const userRoles: string[] = payload.roles || [];
    const userPermissions: string[] = payload.permissions || [];

    // Bypass check for admin
    if (userRoles.includes("admin")) {
      return <>{children}</>;
    }

    // Validate roles match
    const matchesRoles = roles.length === 0 || roles.some(r => userRoles.includes(r));

    // Validate permissions match
    const matchesPermissions = permissions.length === 0 || permissions.some(p => userPermissions.includes(p));

    if (matchesRoles && matchesPermissions) {
      return <>{children}</>;
    }
  } catch (e) {
    // Decoding failed
  }

  return <>{fallback}</>;
};

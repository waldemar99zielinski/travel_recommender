import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Route, Routes, useLocation } from "react-router-dom";

import { AppLayout } from "@/app/layout/AppLayout";
import { ErrorPage } from "@/pages/error/ErrorPage";
import { LoadingPage } from "@/pages/loading/LoadingPage";
import { NotFoundPage } from "@/pages/not-found/NotFoundPage";
import { RecommendationPage } from "@/pages/recommendation/RecommendationPage";
import { TestPage } from "@/pages/test/TestPage";
import { useHealthContext } from "@/shared/context";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "AppRouter" });

export function AppRouter() {
    const { t } = useTranslation();
    const location = useLocation();
    const {
        healthData,
        healthStatus,
        healthError,
        isOperational,
    } = useHealthContext();
    const [hasCompletedInitialLoad, setHasCompletedInitialLoad] =
        useState(false);

    useEffect(() => {
        logger.trace("Route changed", {
            pathname: location.pathname,
            search: location.search,
        });
    }, [location.pathname, location.search]);

    useEffect(() => {
        if (hasCompletedInitialLoad) {
            return;
        }

        if (healthStatus === "idle" || healthStatus === "loading") {
            return;
        }

        if (healthError != null) {
            logger.error("Application health check failed", {
                health: healthData,
                healthError,
            });
            return;
        }

        if (healthData == null) {
            logger.error("Application health check finished without response");
            return;
        }

        if (!isOperational) {
            logger.error("Application health check returned degraded status", {
                healthStatus,
                healthError,
                health: healthData,
            });
            return;
        }

        logger.trace("Application health check passed, marking initial load as completed", {
            healthStatus,
            healthError,
            health: healthData,
        });

        if (!hasCompletedInitialLoad) {
            setHasCompletedInitialLoad(true);
        }
    }, [
        hasCompletedInitialLoad,
        healthData,
        healthError,
        healthStatus,
        isOperational,
    ]);

    if (!hasCompletedInitialLoad) {
        if (healthError != null || !isOperational) {
            return <ErrorPage message={t("error.appNotOperational")} />;
        }

        return <LoadingPage />;
    }

    return (
        <Routes>
            <Route element={<AppLayout />}>
                <Route path="/" element={<RecommendationPage />} />
                <Route path="/test" element={<TestPage />} />
                <Route path="*" element={<NotFoundPage />} />
            </Route>
        </Routes>
    );
}

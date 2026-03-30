import { Route, Routes } from "react-router-dom";

import { AppLayout } from "@/app/layout/AppLayout";
import { NotFoundPage } from "@/pages/not-found/NotFoundPage";
import { RecommendationPage } from "@/pages/recommendation/RecommendationPage";
import { TestPage } from "@/pages/test/TestPage";

export function AppRouter() {
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

import { AppRouter } from "@/app/router/AppRouter";
import { DebugToolsModal } from "@/components/debug/DebugToolsModal";
import { AppContextProvider } from "@/shared/context";

function App() {
    return (
        <AppContextProvider>
            <AppRouter />
            <DebugToolsModal />
        </AppContextProvider>
    );
}

export default App;

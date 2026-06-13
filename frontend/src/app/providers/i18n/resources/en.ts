export const translationEn = {
    app: {
        title: "Hybrid Travel Recommender",
    },
    recommendation: {
        loadingMapData: "Loading map data...",
        noRegionsFound: "No regions were found.",
    },
    chat: {
        emptyState: "Start by sending a message.",
        inputPlaceholder: "Type a message...",
        genericError: "Unable to complete your request right now.",
        send: "Send",
        loading: "Waiting for response",
        typing: "Assistant is typing",
        progress: {
            loadingHistory: "Loading your history...",
            analyzing: "Analyzing your request...",
            searching: "Searching destinations...",
            generatingResponse: "Generating response...",
            saving: "Saving results...",
        },
        recommendations: {
            title: "Top {{count}} results",
            score: "Score: {{score}}/100",
            noDescription: "No description available.",
            knowMore: "Know more about {{region}}",
            destinationResearch: {
                loading: "Loading details",
                ready: "Details ready",
            },
        },
        newSession: {
            action: "New session",
            title: "Start new session?",
            description:
                "This will clear the current conversation and recommendation results, then switch chat to a fresh session.",
            cancel: "Cancel",
            confirm: "Start new session",
        },
        filterSummary: {
            heading: "Region filters",
            included: "{{count}} included",
            excluded: "{{count}} excluded",
            clear: "Clear",
            change: "Change",
            detectedFilters: "Detected preferences",
            regions: "{{count}} regions",
            parentRegions: "Continents / broad regions",
            directRegions: "Specific regions",
            seasonality: "Seasonality",
            budget: "Budget",
        },
    },
    map: {
        mode: {
            browse: "Browse",
            select: "Select",
        },
        draftAction: {
            include: "Include",
            exclude: "Exclude",
            remove: "Remove",
        },
        draftSelectionMenu: {
            exitSelectionMode: "Exit selection mode",
            regionsSelected_one: "{{count}} region selected",
            regionsSelected_other: "{{count}} regions selected",
            clear: "Clear",
        },
        legend: {
            recommended: "Recommended regions",
            included: "Included regions",
            excluded: "Excluded regions",
        },
        popup: {
            regionId: "Region id: {{id}}",
            score: "Score: {{score}}/100",
            noRecommendation:
                "No recommendation available for this region in current results.",
        },
    },
    notFound: {
        title: "Page not found",
        description: "We could not find the page you are looking for.",
        cta: "Go to recommendations",
    },
    error: {
        title: "Something went wrong",
        defaultMessage: "Something went wrong :0",
        appNotOperational:
            "The application is currently not operational. Please try again later.",
    },
    loading: {
        message: "Initializing application...",
    },
    loader: {
        loading: "Loading",
    },
    test: {
        quickReplies: {
            warmBeach: "Warm beach with short flights",
            mountainTown: "Mountain town with lakes",
            familyCityBreak: "Family-friendly city break",
        },
        introMessage:
            "Hi! This is a composed chat preview with predefined text and clickable chat items.",
        clickableMessage: "Click this message to auto-fill a beach request.",
        clickableAutofill: "Suggest a sunny coast destination with easy hikes.",
        quickPicks: "Quick picks:",
        demoReply: 'Noted: "{{message}}". This is a demo reply from the test page.',
        pageTitle: "Component test page",
        pageDescription:
            "Use this page as a sandbox for quickly previewing UI components.",
        chatPreviewTitle: "Composed chat preview",
        chatPreviewDescription:
            "Includes predefined text, clickable message cards, and custom clickable chips embedded in chat history.",
        showLoaderPreview: "Show travel loader preview",
        loaderHidden: "Loader preview is hidden.",
        timerLoaderLabel: "Timed progress loader",
        mapSnippetsTitle: "Map component snippets",
        rankLabelExample: "Rank label example:",
    },
} as const;

export const translationEn = {
    app: {
        title: "Hybrid Travel Recommender",
    },
    recommendation: {
        loadingMapData: "Loading map data...",
    },
    chat: {
        emptyState: "Start by sending a message.",
        inputPlaceholder: "Type a message...",
        send: "Send",
        loading: "...",
    },
    map: {
        legend: {
            excellent: "Excellent",
            good: "Good",
            fair: "Fair",
            uncertain: "Uncertain",
            poor: "Poor",
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
        mapSnippetsTitle: "Map component snippets",
        rankLabelExample: "Rank label example:",
    },
} as const;

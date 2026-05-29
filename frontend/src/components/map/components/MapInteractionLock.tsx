import { useEffect } from "react";

import { useMap } from "react-leaflet";

type MapInteractionLockProps = {
    draggingDisabled: boolean;
};

export function MapInteractionLock({ draggingDisabled }: MapInteractionLockProps) {
    const map = useMap();

    useEffect(() => {
        if (draggingDisabled) {
            map.dragging.disable();
        } else {
            map.dragging.enable();
        }
        return () => {
            map.dragging.enable();
        };
    }, [draggingDisabled, map]);

    return null;
}
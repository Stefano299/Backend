document.addEventListener("DOMContentLoaded", function() {
    const progressLine = document.getElementById("progress-line");
    const items = document.querySelectorAll(".timeline-item");
    
    function updateProgressLine() {
        if (!progressLine || items.length === 0) return;
        
        let activeIndex = -1;
        items.forEach((item, index) => {
            if (item.classList.contains("active")) {
                activeIndex = index;
            } else if (item.classList.contains("completed") && index > activeIndex) {
                activeIndex = index;
            }
        });

        if (activeIndex >= 0) {
            const firstBullet = items[0].querySelector(".timeline-bullet");
            const activeBullet = items[activeIndex].querySelector(".timeline-bullet");
            
            const timeline = document.querySelector(".timeline");
            if (!timeline || !firstBullet || !activeBullet) return;
            
            const timelineRect = timeline.getBoundingClientRect();
            const firstRect = firstBullet.getBoundingClientRect();
            const activeRect = activeBullet.getBoundingClientRect();
            
            const startTop = (firstRect.top + firstRect.height / 2) - timelineRect.top;
            const endTop = (activeRect.top + activeRect.height / 2) - timelineRect.top;
            const height = endTop - startTop;
            
            progressLine.style.top = startTop + "px";
            progressLine.style.height = height + "px";
        } else {
            progressLine.style.height = "0px";
        }
    }
    
    // Wait a tiny bit for render settling/images
    setTimeout(updateProgressLine, 100);
    window.addEventListener("resize", updateProgressLine);
});

package com.sanctuary;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Sanctuary VR Metaverse - Beta Progressive Web Application
 *
 * A web-based VR experience using WebXR that runs in VR browsers
 * (Meta Quest Browser, Firefox Reality, etc.)
 *
 * This Java Spring Boot backend serves:
 * - WebXR frontend (Three.js)
 * - REST API for model generation
 * - WebSocket for multiplayer
 * - Progressive Web App capabilities
 *
 * Lead Architect: Curtis G Kyle Junior
 *
 * @version 0.1.0-BETA
 */
@SpringBootApplication
@EnableCaching
@EnableAsync
public class SanctuaryBetaApplication {

    public static void main(String[] args) {
        printBanner();
        SpringApplication.run(SanctuaryBetaApplication.class, args);
    }

    private static void printBanner() {
        System.out.println("""

                ╔═══════════════════════════════════════════════════════════╗
                ║                                                           ║
                ║         SANCTUARY VR METAVERSE - BETA v0.1.0             ║
                ║                                                           ║
                ║         Progressive Web Application (WebXR)              ║
                ║         Lead Architect: Curtis G Kyle Junior             ║
                ║                                                           ║
                ║         Platform: Java Spring Boot + Three.js            ║
                ║         Target: Meta Quest 3 Browser / PCVR              ║
                ║                                                           ║
                ╚═══════════════════════════════════════════════════════════╝

                Starting Sanctuary Beta Server...

                """);
    }
}

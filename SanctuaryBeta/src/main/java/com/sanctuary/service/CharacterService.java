package com.sanctuary.service;

import com.sanctuary.model.*;
import com.sanctuary.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Character Profile Service - Manages character progression and data
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CharacterService {

    private final CharacterProfileRepository characterProfileRepository;
    private final InventoryItemRepository inventoryItemRepository;
    private final SkillRepository skillRepository;
    private final SpellRepository spellRepository;
    private final AcquiredKnowledgeRepository knowledgeRepository;
    private final CredentialRepository credentialRepository;

    /**
     * Get or create character profile for user
     */
    @Transactional
    public CharacterProfile getOrCreateProfile(User user) {
        return characterProfileRepository.findByUser(user)
                .orElseGet(() -> createDefaultProfile(user));
    }

    /**
     * Create default character profile with starter stats
     */
    private CharacterProfile createDefaultProfile(User user) {
        log.info("Creating default character profile for user: {}", user.getUsername());

        CharacterProfile profile = CharacterProfile.builder()
                .user(user)
                .characterName(user.getUsername())
                .level(1)
                .experience(0)
                .experienceToNextLevel(100)
                .enlightenment(0)
                .wisdom(0)
                .creativity(0)
                .harmony(0)
                .knowledge(0)
                .essencePoints(50) // Starting essence
                .creationTokens(1)  // Starting token
                .meditationMinutes(0)
                .biomesVisited(0)
                .creationsMade(0)
                .textsRead(0)
                .build();

        profile = characterProfileRepository.save(profile);

        // Initialize starter skills
        initializeStarterSkills(profile);

        // Initialize starter spells
        initializeStarterSpells(profile);

        log.info("Created character profile: {} (Level {})", profile.getCharacterName(), profile.getLevel());
        return profile;
    }

    /**
     * Initialize starter skills for new character
     */
    private void initializeStarterSkills(CharacterProfile profile) {
        // Creation skill
        Skill sculpture = Skill.builder()
                .characterProfile(profile)
                .type(Skill.SkillType.SCULPTURE)
                .name("3D Modeling")
                .description("Learn to sculpt and create in VR")
                .level(1)
                .experience(0)
                .experienceToNextLevel(50)
                .isActive(true)
                .build();

        // Meditation skill
        Skill meditation = Skill.builder()
                .characterProfile(profile)
                .type(Skill.SkillType.MEDITATION)
                .name("Mindfulness")
                .description("Develop inner peace and focus")
                .level(1)
                .experience(0)
                .experienceToNextLevel(50)
                .isActive(true)
                .build();

        skillRepository.saveAll(List.of(sculpture, meditation));
        log.info("Initialized starter skills for {}", profile.getCharacterName());
    }

    /**
     * Initialize starter spells for new character
     */
    private void initializeStarterSpells(CharacterProfile profile) {
        // Creation spell
        Spell manifestCreation = Spell.builder()
                .characterProfile(profile)
                .name("Manifest Creation")
                .description("Summon a created object into existence")
                .school(Spell.SpellSchool.CREATION)
                .level(1)
                .essenceCost(25)
                .cooldownSeconds(60)
                .isUnlocked(true)
                .build();

        // Harmony spell
        Spell innerPeace = Spell.builder()
                .characterProfile(profile)
                .name("Inner Peace")
                .description("Restore balance and clarity to the mind")
                .school(Spell.SpellSchool.HARMONY)
                .level(1)
                .essenceCost(15)
                .cooldownSeconds(30)
                .isUnlocked(true)
                .build();

        spellRepository.saveAll(List.of(manifestCreation, innerPeace));
        log.info("Initialized starter spells for {}", profile.getCharacterName());
    }

    /**
     * Get complete character data including all related entities
     */
    @Transactional(readOnly = true)
    public Map<String, Object> getCompleteCharacterData(User user) {
        CharacterProfile profile = getOrCreateProfile(user);

        Map<String, Object> data = new HashMap<>();
        data.put("profile", profile);
        data.put("inventory", inventoryItemRepository.findByCharacterProfile(profile));
        data.put("skills", skillRepository.findByCharacterProfile(profile));
        data.put("spells", spellRepository.findByCharacterProfile(profile));
        data.put("knowledge", knowledgeRepository.findByCharacterProfile(profile));
        data.put("credentials", credentialRepository.findByCharacterProfile(profile));

        return data;
    }

    /**
     * Award experience to character
     */
    @Transactional
    public boolean awardExperience(User user, int amount, String reason) {
        CharacterProfile profile = getOrCreateProfile(user);

        boolean leveledUp = profile.addExperience(amount);
        characterProfileRepository.save(profile);

        log.info("Awarded {} XP to {} (reason: {}). Level up: {}",
                amount, profile.getCharacterName(), reason, leveledUp);

        return leveledUp;
    }

    /**
     * Award experience to a skill
     */
    @Transactional
    public boolean awardSkillExperience(User user, Skill.SkillType skillType, int amount) {
        CharacterProfile profile = getOrCreateProfile(user);

        Skill skill = skillRepository.findByCharacterProfileAndType(profile, skillType)
                .orElseThrow(() -> new RuntimeException("Skill not found: " + skillType));

        boolean leveledUp = skill.addExperience(amount);
        skillRepository.save(skill);

        log.info("Awarded {} XP to skill {} for {}. Level up: {}",
                amount, skillType, profile.getCharacterName(), leveledUp);

        return leveledUp;
    }

    /**
     * Add item to inventory
     */
    @Transactional
    public InventoryItem addInventoryItem(User user, InventoryItem item) {
        CharacterProfile profile = getOrCreateProfile(user);
        item.setCharacterProfile(profile);

        InventoryItem saved = inventoryItemRepository.save(item);
        log.info("Added item {} to {}'s inventory", item.getName(), profile.getCharacterName());

        return saved;
    }

    /**
     * Cast a spell
     */
    @Transactional
    public boolean castSpell(User user, Long spellId) {
        CharacterProfile profile = getOrCreateProfile(user);

        Spell spell = spellRepository.findById(spellId)
                .orElseThrow(() -> new RuntimeException("Spell not found"));

        if (!spell.getCharacterProfile().getId().equals(profile.getId())) {
            throw new RuntimeException("Spell does not belong to this character");
        }

        if (!spell.isReady()) {
            log.warn("Spell {} is not ready to cast", spell.getName());
            return false;
        }

        if (profile.getEssencePoints() < spell.getEssenceCost()) {
            log.warn("Not enough essence to cast {}", spell.getName());
            return false;
        }

        // Deduct essence
        profile.setEssencePoints(profile.getEssencePoints() - spell.getEssenceCost());
        characterProfileRepository.save(profile);

        // Cast spell
        spell.cast();
        spellRepository.save(spell);

        log.info("{} cast {} (Cost: {} essence)", profile.getCharacterName(), spell.getName(), spell.getEssenceCost());
        return true;
    }

    /**
     * Track meditation session
     */
    @Transactional
    public void trackMeditation(User user, int minutes) {
        CharacterProfile profile = getOrCreateProfile(user);

        profile.setMeditationMinutes(profile.getMeditationMinutes() + minutes);

        // Award XP based on meditation time
        int xpGained = minutes * 2;
        profile.addExperience(xpGained);

        // Award Enlightenment stat
        profile.setEnlightenment(profile.getEnlightenment() + (minutes / 5));

        // Award meditation skill XP
        skillRepository.findByCharacterProfileAndType(profile, Skill.SkillType.MEDITATION)
                .ifPresent(skill -> {
                    skill.addExperience(minutes * 5);
                    skillRepository.save(skill);
                });

        characterProfileRepository.save(profile);

        log.info("{} meditated for {} minutes. Gained {} XP",
                profile.getCharacterName(), minutes, xpGained);
    }

    /**
     * Track biome visit
     */
    @Transactional
    public void trackBiomeVisit(User user, String biomeName, int durationSeconds, int nodesVisited) {
        CharacterProfile profile = getOrCreateProfile(user);

        // Check if this is a new biome
        BiomeVisit lastVisit = null; // Would check via BiomeVisitRepository

        profile.setBiomesVisited(profile.getBiomesVisited() + 1);

        // Award XP for exploration
        int xpGained = 50 + (nodesVisited * 10);
        profile.addExperience(xpGained);

        // Award wisdom for learning
        profile.setWisdom(profile.getWisdom() + nodesVisited);

        characterProfileRepository.save(profile);

        log.info("{} visited {} (Duration: {}s, Nodes: {}). Gained {} XP",
                profile.getCharacterName(), biomeName, durationSeconds, nodesVisited, xpGained);
    }

    /**
     * Complete a knowledge entry
     */
    @Transactional
    public void completeKnowledge(User user, Long knowledgeId) {
        CharacterProfile profile = getOrCreateProfile(user);

        AcquiredKnowledge knowledge = knowledgeRepository.findById(knowledgeId)
                .orElseThrow(() -> new RuntimeException("Knowledge entry not found"));

        if (!knowledge.getCharacterProfile().getId().equals(profile.getId())) {
            throw new RuntimeException("Knowledge does not belong to this character");
        }

        if (!knowledge.getIsCompleted()) {
            knowledge.complete();

            // Award XP
            int xpGained = 100;
            knowledge.setExperienceGained(xpGained);
            profile.addExperience(xpGained);

            // Update texts read counter
            profile.setTextsRead(profile.getTextsRead() + 1);

            // Award knowledge stat
            profile.setKnowledge(profile.getKnowledge() + 5);

            knowledgeRepository.save(knowledge);
            characterProfileRepository.save(profile);

            log.info("{} completed knowledge: {}. Gained {} XP",
                    profile.getCharacterName(), knowledge.getTitle(), xpGained);
        }
    }

    /**
     * Update character name
     */
    @Transactional
    public CharacterProfile updateCharacterName(User user, String newName) {
        CharacterProfile profile = getOrCreateProfile(user);
        profile.setCharacterName(newName);
        return characterProfileRepository.save(profile);
    }

    /**
     * Get character statistics summary
     */
    @Transactional(readOnly = true)
    public Map<String, Object> getCharacterStats(User user) {
        CharacterProfile profile = getOrCreateProfile(user);

        Map<String, Object> stats = new HashMap<>();
        stats.put("level", profile.getLevel());
        stats.put("experience", profile.getExperience());
        stats.put("totalCreations", profile.getCreationsMade());
        stats.put("totalMeditation", profile.getMeditationMinutes());
        stats.put("biomesVisited", profile.getBiomesVisited());
        stats.put("textsRead", profile.getTextsRead());
        stats.put("skillCount", skillRepository.findByCharacterProfile(profile).size());
        stats.put("spellCount", spellRepository.findByCharacterProfileAndIsUnlockedTrue(profile).size());
        stats.put("knowledgeCompleted", knowledgeRepository.countByCharacterProfileAndIsCompletedTrue(profile));
        stats.put("verifiedCredentials", credentialRepository.countByCharacterProfileAndVerificationStatus(
                profile, Credential.VerificationStatus.VERIFIED));

        return stats;
    }
}

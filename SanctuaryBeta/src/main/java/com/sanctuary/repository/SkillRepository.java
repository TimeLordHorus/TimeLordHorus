package com.sanctuary.repository;

import com.sanctuary.model.CharacterProfile;
import com.sanctuary.model.Skill;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SkillRepository extends JpaRepository<Skill, Long> {
    List<Skill> findByCharacterProfile(CharacterProfile profile);
    List<Skill> findByCharacterProfileAndIsActiveTrue(CharacterProfile profile);
    Optional<Skill> findByCharacterProfileAndType(CharacterProfile profile, Skill.SkillType type);
}

package com.sanctuary.repository;

import com.sanctuary.model.CharacterProfile;
import com.sanctuary.model.Spell;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SpellRepository extends JpaRepository<Spell, Long> {
    List<Spell> findByCharacterProfile(CharacterProfile profile);
    List<Spell> findByCharacterProfileAndIsUnlockedTrue(CharacterProfile profile);
    List<Spell> findByCharacterProfileAndSchool(CharacterProfile profile, Spell.SpellSchool school);
}

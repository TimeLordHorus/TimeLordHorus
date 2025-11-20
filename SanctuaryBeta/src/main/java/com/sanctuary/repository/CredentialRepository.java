package com.sanctuary.repository;

import com.sanctuary.model.CharacterProfile;
import com.sanctuary.model.Credential;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CredentialRepository extends JpaRepository<Credential, Long> {
    List<Credential> findByCharacterProfile(CharacterProfile profile);
    List<Credential> findByCharacterProfileAndVerificationStatus(CharacterProfile profile, Credential.VerificationStatus status);
    List<Credential> findByCharacterProfileAndIsPublicTrue(CharacterProfile profile);
    long countByCharacterProfileAndVerificationStatus(CharacterProfile profile, Credential.VerificationStatus status);
}

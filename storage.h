#ifndef STORAGE_H
#define STORAGE_H

#define CONFIG_PATH "/config.json"

void initStorage();
void loadProfiles();

String getProfileName(int index);
int getProfileCount();

void runProfile(int index);
bool deleteProfile(int index);
void saveProfiles();

#endif
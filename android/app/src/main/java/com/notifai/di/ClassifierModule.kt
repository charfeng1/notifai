package com.notifai.di

import android.content.Context
import com.notifai.data.repository.FolderRepository
import com.notifai.data.repository.SettingsRepository
import com.notifai.domain.classifier.ClassificationParser
import com.notifai.domain.classifier.LlamaClassifier
import com.notifai.domain.classifier.PromptBuilder
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object ClassifierModule {

    @Provides
    @Singleton
    fun provideLlamaClassifier(@ApplicationContext context: Context): LlamaClassifier =
        LlamaClassifier(context)

    @Provides
    @Singleton
    fun providePromptBuilder(
        folderRepository: FolderRepository,
        settingsRepository: SettingsRepository
    ): PromptBuilder = PromptBuilder(folderRepository, settingsRepository)

    @Provides
    @Singleton
    fun provideClassificationParser(): ClassificationParser = ClassificationParser()
}

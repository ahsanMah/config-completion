package com.vmware.antlr4c3;

import jdk.internal.cmm.SystemResourcePressureImpl;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.BaseErrorListener;
import org.antlr.v4.runtime.atn.ParserATNSimulator;
import org.antlr.v4.runtime.atn.PredictionMode;
import org.batfish.common.BatfishException;
import org.batfish.common.BatfishLogger;
import org.batfish.common.Warnings;
import org.batfish.config.Settings;
import org.batfish.datamodel.ConfigurationFormat;
import org.batfish.grammar.*;
import org.batfish.grammar.cisco.CiscoCombinedParser;
import org.batfish.grammar.cisco.CiscoLexer;
import org.batfish.grammar.cisco.CiscoParser;


import java.lang.reflect.InvocationTargetException;
import java.util.LinkedList;

public class MyTest {


    public static class CountingErrorListener extends BaseErrorListener {

        public int errorCount = 0;

        @Override
        public void syntaxError(Recognizer<?, ?> recognizer, Object offendingSymbol, int line, int charPositionInLine, String msg, RecognitionException e) {
            super.syntaxError(recognizer, offendingSymbol, line, charPositionInLine, msg, e);
            errorCount++;

        }
    }


    /**
     * Format (i.e., domain-specific language)
     */
    private ConfigurationFormat format;

    /**
     * Settings required for using Batfish's lexer/parser
     */
    private static org.batfish.config.Settings batfishSettings;

    /**
     * Warnings settings required for using Batfish's lexer/parser
     */
    private static Warnings batfishWarnings;

    /**
     * Parser and lexer
     */
    private BatfishCombinedParser<?, ?> combinedParser;

    public void test1_simpleExpressionTest() throws Exception {

        System.out.println();
        System.out.println("simpleExpressionTest");

        String expression =
                "!\n" +
                "version 12.4\n" +
                "!\n" +
                "hostname B\n" +
                "!\n" +
                "access-list 1 deny 12.0.0.0 0.255.255.255\n" +
                "access-list 1 permit any\n" +
                "!\n" +
                "interface GigabitEthernet0/1\n" +
                "    description INFRA:C:Gi0/1\n" +
                "    ip address 1.0.1.1 255.255.0.0\n" +
                "    ip ospf cost 1\n" +
                "    ip access-group 1 in\n" +
                "!\n" +
                "interface GigabitEthernet0/2\n" +
                "    description INFRA:D:Gi0/1\n" +
                "    ip address 3.0.1.2 255.255.0.0\n" +
                "    ip ospf cost 1\n" +
                "    ip access-group 1 in\n" +
                "!\n" +
                "interface GigabitEthernet0/3\n" +
                "    ip address 11.0.1.3 255.0.0.0\n" +
                "!\n" +
                "router ospf 1\n" +
                "    redistribute connected\n" +
                "    network 3.0.0.0 0.0.255.255 area 0\n" +
                "    network 1.0.0.0 0.0.255.255 area 0\n" +
                "!\n" +
                "end\n";


        this.format = VendorConfigurationFormatDetector
                .identifyConfigurationFormat(expression);

        if (null == batfishSettings) {
            // Prepare batfish settings
            batfishSettings = new org.batfish.config.Settings();
            batfishSettings.setLogger(new BatfishLogger(
                    batfishSettings.getLogLevel(),
                    batfishSettings.getTimestamp(), System.out));
            Settings.TestrigSettings batfishTestrigSettings = new Settings.TestrigSettings();
            batfishTestrigSettings.setBasePath(null); // FIXME?
            batfishSettings.setActiveTestrigSettings(batfishTestrigSettings);
            batfishSettings.setDisableUnrecognized(true);

            batfishWarnings = new Warnings(false, true, false, true,
                    false, false, false);
        }

        switch (this.format) {
            case CISCO_IOS:
            case CISCO_IOS_XR:
            case CISCO_NX:

//                this.combinedParser = new CiscoCombinedParser(expression,
//                        batfishSettings, this.format);
//                Lexer lexer = this.combinedParser.getLexer();
//
//                CiscoParser parser = (CiscoParser) this.combinedParser.getParser();
//                CharStreams.fromString(expression)


                CiscoLexer lexer; //= new CiscoLexer();
//                CommonTokenStream token_stream = new CommonTokenStream(lexer);
                CiscoParser parser; //= new CiscoParser(token_stream);

                //Building Cisco Parser from scratch
                CodePointCharStream inputStream = CharStreams.fromString(expression);

                try {
                    lexer = new CiscoLexer(inputStream);
                } catch (IllegalArgumentException | SecurityException var8) {
                    throw new BatfishException("Error constructing lexer using reflection", var8);
                }

                CommonTokenStream tokens = new CommonTokenStream(lexer);

                try {
                    parser = new CiscoParser(tokens);
                } catch (IllegalArgumentException | SecurityException var7) {
                    throw new Error(var7);
                }

                //Additonal Batfish Settings
//                ((ParserATNSimulator)parser.getInterpreter()).setPredictionMode(PredictionMode.SLL);
//                BatfishANTLRErrorStrategy.BatfishANTLRErrorStrategyFactory NEWLINE_BASED_RECOVERY = new BatfishANTLRErrorStrategy.BatfishANTLRErrorStrategyFactory(2477, "\n");
//                parser.setInterpreter(new BatfishParserATNSimulator((ParserATNSimulator)parser.getInterpreter()));
//                parser.setErrorHandler(NEWLINE_BASED_RECOVERY.build(expression));
//                lexer.setRecoveryStrategy(new BatfishLexerRecoveryStrategy(lexer, BatfishLexerRecoveryStrategy.WHITESPACE_AND_NEWLINES));



                lexer.removeErrorListeners();
                parser.removeErrorListeners();
                CountingErrorListener errorListener = new CountingErrorListener();
                parser.addErrorListener(errorListener);

                // Specify our entry point
//                parser.cisco_configuration();


//                //Getting all token indices
//                TokenStream tokenStream  = parser.getInputStream();
//                tokenStream.seek(0);
//                LinkedList<Integer> tokens = new LinkedList<>();
//                int offset = 1;
//                while (true) {
//                    Token token = tokenStream.LT(offset++);
////                    System.out.println(token.getTokenIndex() + ":"+ token);
//                    tokens.add(token.getTokenIndex());
//                    if (token.getType() == Token.EOF) {
//                        break;
//                    }
//                }
//                parser.reset();
//                lexer.reset();

                CodeCompletionCore core = new CodeCompletionCore(parser, null, null);

                // 1) At the input start.

                System.out.println("***** Printing Candidates *****");

//                for (Integer index: tokens) {
//                    CodeCompletionCore.CandidatesCollection candidates = core.collectCandidates(index.intValue(), parser.getRuleContext());
//                    System.out.println(candidates);
//                    for (Integer candidate : candidates.tokens.keySet()) {
//                        System.out.println(parser.getVocabulary().getDisplayName(candidate));
//                    }
//                }

                CodeCompletionCore.CandidatesCollection candidates = core.collectCandidates(3, null);
                System.out.println(candidates);

        }

    }

    public static void main (String[] args) {

        try {
            MyTest test = new MyTest();

            test.test1_simpleExpressionTest();
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

}

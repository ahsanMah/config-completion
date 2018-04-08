package com.vmware.antlr4c3;

import java.io.IOException;
import java.util.*;

import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.TokenStream;
import org.antlr.v4.runtime.Vocabulary;
import org.antlr.v4.runtime.atn.ATN;
import org.antlr.v4.runtime.atn.ATNState;
import org.antlr.v4.runtime.atn.PredictionMode;
import org.antlr.v4.runtime.atn.Transition;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.TerminalNodeImpl;
import org.batfish.common.BatfishLogger;
import org.batfish.common.Warnings;
import org.batfish.config.Settings;
import org.batfish.config.Settings.TestrigSettings;
import org.batfish.datamodel.ConfigurationFormat;
import org.batfish.grammar.cisco.CiscoCombinedParser;
import org.batfish.grammar.cisco.CiscoLexer;
import org.batfish.grammar.cisco.CiscoParser;
import org.batfish.grammar.cisco.CiscoParser.Cisco_configurationContext;
import org.omg.PortableInterceptor.SYSTEM_EXCEPTION;
import org.apache.commons.io.FileUtils;

public class Driver {

    private static HashMap<Token, ParserRuleContext> contextMap = new HashMap<>();

    public static void main (String[] args) {
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
		
		/*// Construct lexer and parser directly
        CiscoLexer lexer = new CiscoLexer(CharStreams.fromString(expression));
        CommonTokenStream token_stream = new CommonTokenStream(lexer);
        CiscoParser parser = new CiscoParser(token_stream);
        parser.getInterpreter().setPredictionMode(PredictionMode.SLL);*/


		// Prepare batfish settings
		Settings batfishSettings = new Settings();
		batfishSettings.setLogger(new BatfishLogger(
				batfishSettings.getLogLevel(),
				batfishSettings.getTimestamp(), System.out));
		TestrigSettings batfishTestrigSettings = new TestrigSettings();
		batfishTestrigSettings.setBasePath(null); // FIXME?
		batfishSettings.setActiveTestrigSettings(batfishTestrigSettings);
		batfishSettings.setDisableUnrecognized(true);

		CiscoCombinedParser combined = new CiscoCombinedParser(expression,
                    batfishSettings, ConfigurationFormat.CISCO_IOS);

		CiscoLexer lexer = combined.getLexer();
		CiscoParser parser = combined.getParser();

        // Get all tokens
        TokenStream tokenStream  = parser.getInputStream();
        tokenStream.seek(0);
        List<Token> tokens = new LinkedList<>();
        int offset = 1;
        Token tok = tokenStream.LT(offset++);
        while (tok.getType() != Token.EOF) {
            tokens.add(tok);
            tok = tokenStream.LT(offset++);
            break;
        }
        lexer.reset();

        // Specify our entry point
        lexer.removeErrorListeners();
        parser.removeErrorListeners();
        ParserRuleContext root = parser.cisco_configuration();

        CodeCompletionCore core = new CodeCompletionCore(parser, null, null);

        // 1) At the input start.

        Vocabulary vocabulary = parser.getVocabulary();

        collectCandidates(root, "");
        ArrayList<Token> tokenList = new ArrayList<>(contextMap.keySet());
        tokenList.sort(new Comparator<Token>() {
            @Override
            public int compare(Token o1, Token o2) {
                return o1.getLine() - o2.getLine();
            }
        });
//        System.out.println(tokenList);



//        FileUtils.wr write to file
        System.out.println("Line," + "Token Name," + "Candidates");

        for (Token token: tokenList){

            System.out.print(token.getLine() + "," + token.getText() + ",");
            CodeCompletionCore.CandidatesCollection candidates = core.collectCandidates(token.getTokenIndex(),contextMap.get(token));
//            System.out.println(candidates );

            List<String> tokenCandidates = new LinkedList<String>();
            for (Integer candidate : candidates.tokens.keySet()) {
                tokenCandidates.add(vocabulary.getDisplayName(candidate));
            }
//            Collections.sort(tokenCandidates);
            System.out.println(tokenCandidates);

        }
    }

    private static void collectCandidates(ParserRuleContext context, String indent) {
        if (context.getChildCount() > 0) {
//            System.out.println(indent + context.getRuleIndex());

            int terminalChildren = 0;
            for (int i = 0; i < context.getChildCount(); i++) {
                ParseTree childTree = context.getChild(i);
                if (childTree instanceof ParserRuleContext) {
                    ParserRuleContext childContext = 
                            (ParserRuleContext)childTree;
                    collectCandidates(childContext, indent + "  ");
                } else if (childTree instanceof TerminalNodeImpl) {
                    terminalChildren++;
                }
            }

            if (terminalChildren > 0) {
                Token startToken = context.getStart();
                Token stopToken = context.getStop();
                contextMap.put(startToken, context);
//                System.out.println(indent + "BASE\t" + context + "\t" + startToken + "\t" + stopToken);
            }
        }
    }
}
